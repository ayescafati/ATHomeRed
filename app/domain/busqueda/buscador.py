# from __future__ import annotations
# from dataclasses import dataclass, field
# from typing import List
# from .estrategia import EstrategiaBusqueda
# from ..modelos.catalogo import FiltroBusqueda, Publicacion
# from ..modelos.usuarios import Profesional


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


from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from .estrategia import EstrategiaBusqueda
from ..modelos.catalogo import FiltroBusqueda, Publicacion
from ..modelos.usuarios import Profesional

@dataclass
class Buscador:
    estrategia: EstrategiaBusqueda
    profesionales: List[Profesional] = field(default_factory=list)
    publicaciones: List[Publicacion] = field(default_factory=list)

    def set_fuente(
        self,
        profesionales: List[Profesional],
        publicaciones: List[Publicacion],
    ) -> None:
        # Fuente en memoria; en futuro, esto puede venir de un repositorio/ORM
        self.profesionales = profesionales or []
        self.publicaciones = publicaciones or []

    def cambiar_estrategia(self, e: EstrategiaBusqueda) -> None:
        self.estrategia = e

    def buscar(self, filtro: FiltroBusqueda) -> List[Profesional]:
        # Delegamos en la Strategy, con las fuentes cargadas
        return self.estrategia.buscar(
            filtro=filtro,
            profesionales=self.profesionales,
            publicaciones=self.publicaciones,
        )
