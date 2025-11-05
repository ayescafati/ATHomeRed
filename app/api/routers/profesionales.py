"""
Router para gestión de profesionales
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import (
    ProfesionalCreate,
    ProfesionalResponse,
    ProfesionalUpdate
)
from app.api.dependencies import get_profesional_repository
from app.infra.repositories.profesional_repository import ProfesionalRepository
from app.domain.entities.usuarios import Profesional
from app.domain.value_objects.objetos_valor import Ubicacion, Disponibilidad, Matricula
from app.domain.enumeraciones import DiaSemana

router = APIRouter()


# Endpoints

@router.post("/", response_model=ProfesionalResponse, status_code=status.HTTP_201_CREATED)
def crear_profesional(
    data: ProfesionalCreate,
    repo: ProfesionalRepository = Depends(get_profesional_repository)
):
    """
    Crea un nuevo profesional en el sistema.
    """
    try:
        # Convertir schema a entidad de dominio
        ubicacion = Ubicacion(
            provincia=data.ubicacion.provincia,
            departamento=data.ubicacion.departamento,
            barrio=data.ubicacion.barrio,
            calle=data.ubicacion.calle,
            numero=data.ubicacion.numero,
            latitud=data.ubicacion.latitud,
            longitud=data.ubicacion.longitud
        )
        
        # TODO: Obtener especialidades desde el repo de catálogo
        especialidades = []
        
        # Convertir disponibilidades
        disponibilidades = [
            Disponibilidad(
                dias_semana=[DiaSemana(d) for d in disp.dias_semana],
                hora_inicio=disp.hora_inicio,
                hora_fin=disp.hora_fin
            )
            for disp in (data.disponibilidades or [])
        ]
        
        # Convertir matrículas
        matriculas = [
            Matricula(
                numero=mat.numero,
                provincia=mat.provincia,
                vigente_desde=mat.vigente_desde,
                vigente_hasta=mat.vigente_hasta
            )
            for mat in (data.matriculas or [])
        ]
        
        # Crear entidad de dominio
        from uuid import uuid4
        profesional = Profesional(
            id=uuid4(),
            nombre=data.nombre,
            apellido=data.apellido,
            email=data.email,
            celular=data.celular or "",
            ubicacion=ubicacion,
            activo=True,
            verificado=False,
            especialidades=especialidades,
            disponibilidades=disponibilidades,
            matriculas=matriculas
        )
        
        # Guardar en el repositorio
        profesional_creado = repo.crear(profesional)
        
        return profesional_creado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear profesional: {str(e)}"
        )


@router.get("/{profesional_id}", response_model=ProfesionalResponse)
def obtener_profesional(
    profesional_id: UUID,
    repo: ProfesionalRepository = Depends(get_profesional_repository)
):
    """
    Obtiene un profesional por su ID.
    """
    profesional = repo.obtener_por_id(profesional_id)
    
    if not profesional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesional con ID {profesional_id} no encontrado"
        )
    
    return profesional


@router.get("/", response_model=List[ProfesionalResponse])
def listar_profesionales(
    solo_activos: bool = True,
    repo: ProfesionalRepository = Depends(get_profesional_repository)
):
    """
    Lista todos los profesionales activos.
    """
    if solo_activos:
        profesionales = repo.listar_activos()
    else:
        profesionales = repo.listar_todos()
    
    return profesionales


@router.put("/{profesional_id}", response_model=ProfesionalResponse)
def actualizar_profesional(
    profesional_id: UUID,
    data: ProfesionalUpdate,
    repo: ProfesionalRepository = Depends(get_profesional_repository)
):
    """
    Actualiza los datos de un profesional.
    """
    profesional = repo.obtener_por_id(profesional_id)
    
    if not profesional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesional con ID {profesional_id} no encontrado"
        )
    
    if data.nombre is not None:
        profesional.nombre = data.nombre
    if data.apellido is not None:
        profesional.apellido = data.apellido
    if data.celular is not None:
        profesional.celular = data.celular

    if data.ubicacion is not None:
        profesional.ubicacion = Ubicacion(
            provincia=data.ubicacion.provincia,
            departamento=data.ubicacion.departamento,
            barrio=data.ubicacion.barrio,
            calle=data.ubicacion.calle,
            numero=data.ubicacion.numero,
            latitud=data.ubicacion.latitud,
            longitud=data.ubicacion.longitud
        )

    profesional_actualizado = repo.actualizar(profesional)

    return profesional_actualizado


@router.delete("/{profesional_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_profesional(
    profesional_id: UUID,
    repo: ProfesionalRepository = Depends(get_profesional_repository)
):
    """
    Desactiva un profesional (soft delete).
    """
    profesional = repo.obtener_por_id(profesional_id)
    
    if not profesional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesional con ID {profesional_id} no encontrado"
        )
    
    profesional.desactivar()
    
    return None


@router.post("/{profesional_id}/verificar", response_model=ProfesionalResponse)
def verificar_profesional(
    profesional_id: UUID,
    repo: ProfesionalRepository = Depends(get_profesional_repository)
):
    """
    Marca un profesional como verificado.
    Requiere permisos de administrador (TODO: agregar autenticación).
    """
    profesional = repo.obtener_por_id(profesional_id)
    
    if not profesional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesional con ID {profesional_id} no encontrado"
        )
    
    # TODO: Implementar verificación en el dominio y repositorio
    # profesional.verificar()
    # repo.actualizar(profesional)
    
    return profesional
