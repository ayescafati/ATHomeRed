"""
Router para gestión de consultas/citas médicas
"""

from typing import List
from uuid import UUID, uuid4
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import ConsultaCreate, ConsultaResponse, ConsultaUpdate
from app.api.dependencies import (
    get_consulta_repository,
    get_profesional_repository,
    get_paciente_repository,
)
from app.infra.repositories.consulta_repository import ConsultaRepository
from app.infra.repositories.profesional_repository import ProfesionalRepository
from app.infra.repositories.paciente_repository import PacienteRepository
from app.domain.entities.agenda import Cita
from app.domain.enumeraciones import EstadoCita
from app.domain.value_objects.objetos_valor import Ubicacion

router = APIRouter()


@router.post(
    "/", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED
)
def crear_consulta(
    data: ConsultaCreate,
    repo: ConsultaRepository = Depends(get_consulta_repository),
    prof_repo: ProfesionalRepository = Depends(get_profesional_repository),
    pac_repo: PacienteRepository = Depends(get_paciente_repository),
):
    """
    Crea una nueva consulta médica.

    - Verifica que profesional y paciente existan
    - Crea la cita en estado PENDIENTE
    - TODO: Validar disponibilidad del profesional
    - TODO: Aplicar estrategia de asignación (ver domain/strategies)
    - TODO: Notificar a los observadores (ver domain/observers)
    """
    try:
        # Validar que el profesional existe
        profesional = prof_repo.obtener_por_id(data.profesional_id)
        if not profesional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profesional con ID {data.profesional_id} no encontrado",
            )

        # Validar que el paciente existe
        paciente = pac_repo.obtener_por_id(data.paciente_id)
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {data.paciente_id} no encontrado",
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

        # Guardar en el repositorio (necesitamos direccion_id)
        # TODO: Crear dirección desde ubicación
        from app.infra.repositories.direccion_repository import (
            DireccionRepository,
        )
        from app.api.dependencies import get_db

        # Por ahora, usar la dirección del profesional
        cita_creada = repo.crear(
            cita,
            direccion_id=(
                profesional.ubicacion.id
                if hasattr(profesional.ubicacion, "id")
                else None
            ),
        )

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
):
    """
    Confirma una consulta pendiente.
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
):
    """
    Cancela una consulta.
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

        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
