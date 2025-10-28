from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from app.domain.entities.usuarios import Profesional 
from app.domain.entities.catalogo import FiltroBusqueda
from app.infra.repositories.profesional_repository import ProfesionalORM, UbicacionORM, EspecialidadORM

# Desventajas:

# Se rompe la separación de responsabilidades (la estrategia ahora conoce la base de datos).

# Lógica duplicada si en otros lados querés convertir ORM → dominio.

# Difícil de mantener si la estructura del ORM cambia.

class EstrategiaBusqueda(ABC):
    @abstractmethod
    def buscar(self, db: Session, filtro: FiltroBusqueda) -> List[Profesional]:
        pass

class BusquedaPorZona(EstrategiaBusqueda):
    def buscar(self, db: Session, filtro: FiltroBusqueda) -> List[Profesional]:
        
        if filtro.departamento and not filtro.provincia:
            raise ValueError("Se debe especificar la provincia si se indica el departamento.")
        if filtro.barrio and not filtro.departamento:
            raise ValueError("Se debe especificar el departamento si se indica el barrio.")
        
        query = db.query(ProfesionalORM).join(ProfesionalORM.ubicaciuon)

        if filtro.provincia:
            query = query.filter(UbicacionORM.provincia == filtro.provincia)
        if filtro.departamento:
            query = query.filter(UbicacionORM.departamento == filtro.departamento)
        if filtro.barrio:
            query = query.filter(UbicacionORM.barrio == filtro.barrio)

        return query.all()


class BusquedaPorEspecialidad(EstrategiaBusqueda):
    def buscar(self, db: Session, filtro: FiltroBusqueda) -> List[Profesional]:
        
        if not filtro.id_especialidad and not filtro.nombre_especialidad:
            raise ValueError("Se debe especificar al menos un criterio de especialidad.")
        
        query = db.query(ProfesionalORM).join(ProfesionalORM.especialidades)

        if filtro.id_especialidad:
            query = query.filter(EspecialidadORM.id == filtro.id_especialidad) 
            query = query.filter(EspecialidadORM.nombre.ilike(f"%{filtro.nombre_especialidad}%"))

        return query.all()


class BusquedaCombinada(EstrategiaBusqueda):
    def buscar(self, db: Session, filtro: FiltroBusqueda) -> List[Profesional]:  

        if filtro.departamento and not filtro.provincia:
            raise ValueError("Se debe especificar la provincia para poder indicar el departamento.")
        if filtro.barrio and not filtro.departamento:
            raise ValueError("Se debe especificar el departamento para poder indicar el barrio.")

        query = db.query(ProfesionalORM).join(ProfesionalORM.ubicacion)  

        if filtro.provincia:
            query = query.filter(UbicacionORM.provincia == filtro.provincia)
        if filtro.departamento:
            query = query.filter(UbicacionORM.departamento == filtro.departamento)
        if filtro.barrio:
            query = query.filter(UbicacionORM.barrio == filtro.barrio)

        if filtro.id_especialidad or filtro.nombre_especialidad:
            query = query.join(ProfesionalORM.especialidades)
            if filtro.id_especialidad:
                query = query.filter(EspecialidadORM.id == filtro.id_especialidad)
            if filtro.nombre_especialidad:
                query = query.filter(EspecialidadORM.nombre.ilike(f"%{filtro.nombre_especialidad}%"))

        if filtro.texto:
            query = query.filter(
                ProfesionalORM.nombre.ilike(f"%{filtro.texto}%") |
                ProfesionalORM.apellido.ilike(f"%{filtro.texto}%")
            )

        return query.all()
    



# class EstrategiaBusqueda(ABC):
#     @abstractmethod
#     def buscar(
#         self,
#         filtro: FiltroBusqueda,
#         profesionales: List[Profesional],
#         publicaciones: List[Publicacion],
#     ) -> List[Profesional]:
#         pass


# class BusquedaPorZona(EstrategiaBusqueda):
#     def buscar(
#         self,
#         filtro: FiltroBusqueda,
#         profesionales: List[Profesional],
#         publicaciones: List[Publicacion],
#     ) -> List[Profesional]:
#         pass


# class BusquedaPorEspecialidad(EstrategiaBusqueda):
#     def buscar(
#         self,
#         filtro: FiltroBusqueda,
#         profesionales: List[Profesional],
#         publicaciones: List[Publicacion],
#     ) -> List[Profesional]:
#         pass


# class BusquedaCombinada(EstrategiaBusqueda):
#     def buscar(
#         self,
#         filtro: FiltroBusqueda,
#         profesionales: List[Profesional],
#         publicaciones: List[Publicacion],
#     ) -> List[Profesional]:
#         pass

