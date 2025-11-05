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
from app.domain.strategies.buscador import BuscadorProfesionales

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
        # Obtener todos los profesionales según filtros básicos
        profesionales = repo.listar_activos() if criterios.solo_activos else []
        
        # TODO: Implementar BuscadorProfesionales del dominio
        # buscador = BuscadorProfesionales()
        # resultados = buscador.buscar(profesionales, criterios)
        
        criterios_aplicados = {
            "especialidad_id": criterios.especialidad_id,
            "provincia": criterios.provincia,
            "departamento": criterios.departamento,
            "dia_semana": criterios.dia_semana,
            "solo_verificados": criterios.solo_verificados,
            "solo_activos": criterios.solo_activos
        }
        
        # Filtrar solo verificados si se solicita
        if criterios.solo_verificados:
            profesionales = [p for p in profesionales if p.verificado]
        
        return BusquedaProfesionalResponse(
            profesionales=profesionales,
            total=len(profesionales),
            criterios_aplicados=criterios_aplicados
        )
        
    except Exception as e:
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
            {"id": 1, "nombre": "Acompañamiento Terapéutico"},
            {"id": 2, "nombre": "Enfermería"},
            {"id": 3, "nombre": "Enfermería"},
            {"id": 4, "nombre": "Acompañamiento Terapéutico"},
            {"id": 5, "nombre": "Acompañamiento Terapéutico"},
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
