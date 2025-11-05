"""
Router para búsqueda de profesionales
Implementa las estrategias de búsqueda del dominio
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import (
    BusquedaProfesionalRequest,
    BusquedaProfesionalResponse,
    ProfesionalResponse
)
from app.api.dependencies import get_profesional_repository
from app.infra.repositories.profesional_repository import ProfesionalRepository
# from app.domain.strategies.buscador import BuscadorProfesionales

from app.domain.entities.catalogo import FiltroBusqueda
from app.domain.strategies.buscador import Buscador
from app.domain.strategies.estrategia import (
    BusquedaPorZona,
    BusquedaPorEspecialidad,
    BusquedaCombinada
)

router = APIRouter()


@router.post("/profesionales", response_model=BusquedaProfesionalResponse)
def buscar_profesionales(
    criterios: BusquedaProfesionalRequest,
    repo: ProfesionalRepository = Depends(get_profesional_repository)
):
    """
    Busca profesionales según múltiples criterios.
    
    Utiliza el patrón Strategy del dominio para aplicar filtros:
    - Por especialidad
    - Por ubicación (provincia/departamento)
    - Por disponibilidad (día de la semana)
    - Solo verificados/activos
    """

    try:
        filtro = FiltroBusqueda(
            id_especialidad = criterios.especialidad_id,
            nombre_especialidad = criterios.nombre_especialidad,
            provincia = criterios.provincia,
            departamento = criterios.departamento,
            barrio = criterios.barrio,
        )

        if(filtro.id_especialidad or filtro.nombre_especialidad) and (filtro.provincia or filtro.departamento or filtro.barrio):
            estrategia = BusquedaCombinada()
        elif(filtro.id_especialidad or filtro.nombre_especialidad):
            estrategia = BusquedaPorEspecialidad()
        elif(filtro.provincia or filtro.departamento or filtro.barrio):
            estrategia = BusquedaPorZona()
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se debe especificar un criterio de búsqueda válido."
            )

        buscador = Buscador(repo, estrategia)
        profesionales = buscador.buscar(filtro)

        return  BusquedaProfesionalResponse(
            profesionales=profesionales,
            total=len(profesionales),
            criterios_aplicados = filtro.__dict__       
        )
    
    except ValueError as ve:
        # Errores de validación de filtros (de las estrategias)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        # Otros errores inesperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}"
        )

@router.get("/especialidades")
def listar_especialidades():
    """
    Lista todas las especialidades disponibles.
    """
    # TODO: Implementar con repositorio de catálogo
    return {
        "especialidades": [
            {"id": 1, "nombre": "Enfermería"},
            {"id": 2, "nombre": "Kinesiología"},
            {"id": 3, "nombre": "Medicina General"},
            {"id": 4, "nombre": "Pediatría"},
            {"id": 5, "nombre": "Geriatría"}
        ]
    }


@router.get("/ubicaciones/provincias")
def listar_provincias():
    """
    Lista todas las provincias disponibles.
    """
    # TODO: Implementar con repositorio de catálogo
    return {
        "provincias": [
            "Buenos Aires",
            "Córdoba",
            "Santa Fe",
            "Mendoza",
            "Tucumán"
        ]
    }
