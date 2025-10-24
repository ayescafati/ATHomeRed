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
        pass

    def cambiar_estrategia(self, e: EstrategiaBusqueda) -> None:
        pass

    def buscar(self, filtro: FiltroBusqueda) -> List[Profesional]:
        pass
