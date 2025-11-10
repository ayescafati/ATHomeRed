"""
Router para gestión de consultas/citas médicas
"""

from typing import List
from uuid import UUID, uuid4
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas import ConsultaCreate, ConsultaResponse, ConsultaUpdate
from app.api.dependencies import (
    get_consulta_repository,
    get_profesional_repository,
    get_paciente_repository,
    get_db,
)
from app.api.event_bus import get_event_bus
from app.api.policies import IntegrityPolicies
from app.infra.repositories.consulta_repository import ConsultaRepository
from app.infra.repositories.profesional_repository import ProfesionalRepository
from app.infra.repositories.paciente_repository import PacienteRepository
from app.infra.repositories.direccion_repository import DireccionRepository
from app.domain.entities.agenda import Cita
from app.domain.enumeraciones import EstadoCita
from app.domain.value_objects.objetos_valor import Ubicacion
from app.domain.eventos import (
    CitaCreada,
    CitaConfirmada,
    CitaCancelada,
    CitaCompletada,
    CitaReprogramada,
)
from app.domain.observers.observadores import EventBus

router = APIRouter()


@router.post(
    "/", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED
)
def crear_consulta(
    data: ConsultaCreate,
    repo: ConsultaRepository = Depends(get_consulta_repository),
    prof_repo: ProfesionalRepository = Depends(get_profesional_repository),
    pac_repo: PacienteRepository = Depends(get_paciente_repository),
    db: Session = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Crea una nueva consulta/cita en estado PENDIENTE.

    Valida:
    - Profesional verificado y activo
    - Paciente pertenece al solicitante
    - Solicitante activo
    - Disponibilidad horaria (evita solapamientos)
    - Fecha y horarios válidos

    Publica evento CitaCreada en el EventBus para notificaciones.
    """
    try:
        policies = IntegrityPolicies()

        # POLICY 1: Validar que el profesional es VERIFICADO y ACTIVO
        profesional = prof_repo.obtener_por_id(data.profesional_id)
        if not profesional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profesional con ID {data.profesional_id} no encontrado",
            )
        policies.validar_profesional_disponible(db, data.profesional_id)

        # POLICY 2: Validar que el paciente existe y pertenece al solicitante
        paciente = pac_repo.obtener_por_id(data.paciente_id)
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {data.paciente_id} no encontrado",
            )

        # POLICY 3: Validar que el solicitante que crea la cita es el dueño del paciente
        policies.validar_solicitante_es_dueno(
            db, data.paciente_id, data.solicitante_id
        )

        # POLICY 4: Validar que el solicitante está activo
        policies.validar_usuario_activo(db, data.solicitante_id)

        # VALIDACIONES DE NEGOCIO
        # Validación 1: Hora fin debe ser posterior a hora inicio
        if data.hora_fin <= data.hora_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La hora de fin debe ser posterior a la hora de inicio",
            )

        # Validación 2: No permitir citas en fechas pasadas
        if data.fecha < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden crear consultas en fechas pasadas",
            )

        # Validación 3: Verificar disponibilidad (anti-double booking)
        consultas_existentes = repo.listar_por_profesional(
            profesional_id=data.profesional_id,
            desde=data.fecha,
            hasta=data.fecha,
            solo_activas=True,
        )

        for c in consultas_existentes:
            # Detectar solapamiento de horarios
            if (data.hora_inicio < c.hora_fin) and (
                data.hora_fin > c.hora_inicio
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El profesional no está disponible en el horario seleccionado",
                )

        # Crear ubicación
        ubicacion = Ubicacion(
            provincia=data.ubicacion.provincia,
            departamento=data.ubicacion.departamento,
            barrio=data.ubicacion.barrio,
            calle=data.ubicacion.calle,
            numero=data.ubicacion.numero,
            latitud=data.ubicacion.latitud,
            longitud=data.ubicacion.longitud,
        )

        # Crear cita
        cita = Cita(
            id=uuid4(),
            profesional_id=data.profesional_id,
            paciente_id=data.paciente_id,
            fecha=data.fecha,
            hora_inicio=data.hora_inicio,
            hora_fin=data.hora_fin,
            ubicacion=ubicacion,
            estado=EstadoCita.PENDIENTE,
            motivo_consulta=data.motivo or "",
            notas="",
        )

        # Guardar en el repositorio (crear dirección desde ubicación)
        # Por ahora, usar la dirección del profesional
        cita_creada = repo.crear(
            cita,
            direccion_id=(
                profesional.ubicacion.id
                if hasattr(profesional.ubicacion, "id")
                else None
            ),
        )

        # PUBLICAR EVENTO: CitaCreada
        # El EventBus notificará automáticamente a todos los observadores
        evento = CitaCreada(
            cita_id=cita_creada.id,
            profesional_id=data.profesional_id,
            paciente_id=data.paciente_id,
            solicitante_id=data.solicitante_id,
        )
        event_bus.publicar(evento)

        return cita_creada

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear consulta: {str(e)}",
        )


@router.get("/{consulta_id}", response_model=ConsultaResponse)
def obtener_consulta(
    consulta_id: UUID,
    repo: ConsultaRepository = Depends(get_consulta_repository),
):
    """
    Obtiene una consulta por su ID.
    """
    consulta = repo.obtener_por_id(consulta_id)

    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consulta con ID {consulta_id} no encontrada",
        )

    return consulta


@router.get(
    "/profesional/{profesional_id}", response_model=List[ConsultaResponse]
)
def listar_consultas_profesional(
    profesional_id: UUID,
    desde: date = None,
    hasta: date = None,
    solo_activas: bool = False,
    repo: ConsultaRepository = Depends(get_consulta_repository),
):
    """
    Lista todas las consultas de un profesional.

    - desde: Fecha inicial (opcional)
    - hasta: Fecha final (opcional)
    - solo_activas: Si True, excluye canceladas y completadas
    """
    consultas = repo.listar_por_profesional(
        profesional_id, desde=desde, hasta=hasta, solo_activas=solo_activas
    )

    return consultas


@router.get("/paciente/{paciente_id}", response_model=List[ConsultaResponse])
def listar_consultas_paciente(
    paciente_id: UUID,
    desde: date = None,
    solo_activas: bool = False,
    repo: ConsultaRepository = Depends(get_consulta_repository),
):
    """
    Lista todas las consultas de un paciente.

    - desde: Fecha inicial (opcional)
    - solo_activas: Si True, excluye canceladas y completadas
    """
    consultas = repo.listar_por_paciente(
        paciente_id, desde=desde, solo_activas=solo_activas
    )

    return consultas


@router.put("/{consulta_id}", response_model=ConsultaResponse)
def actualizar_consulta(
    consulta_id: UUID,
    data: ConsultaUpdate,
    repo: ConsultaRepository = Depends(get_consulta_repository),
):
    """
    Actualiza una consulta existente.
    Solo permite actualizar fecha, horarios y notas si la consulta no está completada/cancelada.
    """
    consulta = repo.obtener_por_id(consulta_id)

    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consulta con ID {consulta_id} no encontrada",
        )

    if not consulta.puede_modificarse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede modificar una consulta en estado {consulta.estado.value}",
        )

    try:
        # Actualizar campos permitidos
        if data.fecha:
            consulta.fecha = data.fecha
        if data.hora_inicio:
            consulta.hora_inicio = data.hora_inicio
        if data.hora_fin:
            consulta.hora_fin = data.hora_fin
        if data.motivo:
            consulta.motivo_consulta = data.motivo
        if data.notas:
            consulta.notas = data.notas

        consulta_actualizada = repo.actualizar(consulta)

        if not consulta_actualizada:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar consulta",
            )

        return consulta_actualizada

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/{consulta_id}/confirmar", response_model=ConsultaResponse)
def confirmar_consulta(
    consulta_id: UUID,
    repo: ConsultaRepository = Depends(get_consulta_repository),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Confirma una consulta pendiente.
    Publica evento CitaConfirmada en el EventBus para notificaciones.
    """
    consulta = repo.obtener_por_id(consulta_id)

    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consulta con ID {consulta_id} no encontrada",
        )

    try:
        consulta.confirmar()
        consulta_actualizada = repo.actualizar(consulta)

        # PUBLICAR EVENTO: CitaConfirmada
        evento = CitaConfirmada(cita_id=consulta_id)
        event_bus.publicar(evento)

        return consulta_actualizada

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_consulta(
    consulta_id: UUID,
    motivo: str = None,
    repo: ConsultaRepository = Depends(get_consulta_repository),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Cancela una consulta.
    Publica evento CitaCancelada en el EventBus para notificaciones.
    """
    consulta = repo.obtener_por_id(consulta_id)

    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consulta con ID {consulta_id} no encontrada",
        )

    try:
        consulta.cancelar(motivo=motivo)
        repo.actualizar(consulta)

        # PUBLICAR EVENTO: CitaCancelada
        evento = CitaCancelada(cita_id=consulta_id, motivo=motivo)
        event_bus.publicar(evento)

        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/{consulta_id}/completar", response_model=ConsultaResponse)
def completar_consulta(
    consulta_id: UUID,
    notas_finales: str = None,
    repo: ConsultaRepository = Depends(get_consulta_repository),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Marca una consulta confirmada como completada.
    Publica evento CitaCompletada en el EventBus para notificaciones.
    """
    consulta = repo.obtener_por_id(consulta_id)

    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consulta con ID {consulta_id} no encontrada",
        )

    try:
        consulta.completar(notas_finales=notas_finales)
        consulta_actualizada = repo.actualizar(consulta)

        # PUBLICAR EVENTO: CitaCompletada
        evento = CitaCompletada(cita_id=consulta_id, notas=notas_finales)
        event_bus.publicar(evento)

        return consulta_actualizada

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/{consulta_id}/reprogramar", response_model=ConsultaResponse)
def reprogramar_consulta(
    consulta_id: UUID,
    data: ConsultaUpdate,
    repo: ConsultaRepository = Depends(get_consulta_repository),
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Reprograma una consulta (cambia fecha y horarios).
    Publica evento CitaReprogramada en el EventBus para notificaciones.
    """
    consulta = repo.obtener_por_id(consulta_id)

    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consulta con ID {consulta_id} no encontrada",
        )

    if not data.fecha or not data.hora_inicio or not data.hora_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Para reprogramar se requiere fecha, hora_inicio y hora_fin",
        )

    try:
        # Guardar valores anteriores para el evento
        fecha_anterior = f"{consulta.fecha} {consulta.hora_inicio}-{consulta.hora_fin}"
        
        consulta.reprogramar(
            nueva_fecha=data.fecha,
            nueva_hora_inicio=data.hora_inicio,
            nueva_hora_fin=data.hora_fin,
        )
        consulta_actualizada = repo.actualizar(consulta)

        # PUBLICAR EVENTO: CitaReprogramada
        fecha_nueva = f"{data.fecha} {data.hora_inicio}-{data.hora_fin}"
        evento = CitaReprogramada(
            cita_id=consulta_id,
            fecha_anterior=fecha_anterior,
            fecha_nueva=fecha_nueva,
        )
        event_bus.publicar(evento)

        return consulta_actualizada

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
