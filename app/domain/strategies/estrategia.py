from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from app.domain.entities.catalogo import FiltroBusqueda
from app.domain.entities.usuarios import Profesional
from app.infra.repositories.profesional_repository import ProfesionalRepository
from .estrategia import EstrategiaBusqueda

@dataclass
class Buscador:
    repo: ProfesionalRepository
    estrategia: EstrategiaBusqueda
    profesionales: list[Profesional] = field(default_factory=list)

    def cambiar_estrategia(self, estrategia: EstrategiaBusqueda) -> None:
        self.estrategia = estrategia
    
    def buscar(self, filtro: FiltroBusqueda) -> list[Profesional]:
        self.profesionales = self.estrategia.buscar(self.repo, filtro)
        return self.profesionales
    

# @dataclass
# class Buscador:
#     estrategia: EstrategiaBusqueda
#     profesionales: List[Profesional] = field(default_factory=list)
#     publicaciones: List[Publicacion] = field(default_factory=list)

#     def set_fuente(
#         self,
#         profesionales: List[Profesional],
#         publicaciones: List[Publicacion],
#     ) -> None:
#         pass

#     def cambiar_estrategia(self, e: EstrategiaBusqueda) -> None:
#         pass

#     def buscar(self, filtro: FiltroBusqueda) -> List[Profesional]:
#         pass