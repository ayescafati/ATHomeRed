from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from app.domain.entities.usuarios import Profesional 
from app.domain.entities.catalogo import FiltroBusqueda
from app.infra.repositories.profesional_repository import ProfesionalRepository

# Desventajas:

# Se rompe la separación de responsabilidades (la estrategia ahora conoce la base de datos).

# Lógica duplicada si en otros lados querés convertir ORM → dominio.

# Difícil de mantener si la estructura del ORM cambia.


class EstrategiaBusqueda(ABC):
    @abstractmethod
    def buscar(self, repo: ProfesionalRepository, filtro: FiltroBusqueda) -> List[Profesional]:
        pass

class BusquedaPorZona(EstrategiaBusqueda):
    def buscar(self, repo: ProfesionalRepository, filtro: FiltroBusqueda) -> list[Profesional]:
        if filtro.departamento and not filtro.provincia:
            raise ValueError("Se debe especificar la provincia si se indica el departamento.")
        if filtro.barrio and not filtro.departamento:
            raise ValueError("Se debe especificar el departamento si se indica el barrio.")
        
        # La logica de filtrado se delega al repositorio
        return repo.buscar_por_ubicacion(
            provincia = filtro.provincia,
            departamento = filtro.departamento,
            barrio = filtro.barrio
        )

class BusquedaPorEspecialidad(EstrategiaBusqueda):
    def buscar(self, repo: ProfesionalRepository, filtro: FiltroBusqueda) -> list[Profesional]:
        if not filtro.id_especialidad and not filtro.nombre_especialidad:
            raise ValueError("Se debe especificar al menos un criterio de especialidad.")
        
        especialidad = filtro.nombre_especialidad 
        return repo.buscar_por_especialidad(especialidad)
    
class BusquedaCombinada(EstrategiaBusqueda):
    def buscar(self, repo: ProfesionalRepository, filtro: FiltroBusqueda) -> list[Profesional]:
        if filtro.departamento and not filtro.provincia:
            raise ValueError("Se debe especificar la provincia si se indica el departamento.")
        if filtro.barrio and not filtro.departamento:
            raise ValueError("Se debe especificar el departamento si se indica el barrio.")
        if not filtro.id_especialidad and not filtro.nombre_especialidad:
            raise ValueError("Se debe especificar al menos un criterio de especialidad.")
        
        especialidad = filtro.nombre_especialidad 
        return repo.buscar_combinado(especialidad,
            provincia=filtro.provincia,
            departamento=filtro.departamento,
            barrio=filtro.barrio
        )
