# from __future__ import annotations
# from abc import ABC, abstractmethod
# from typing import List
# from ..modelos.catalogo import FiltroBusqueda, Publicacion
# from ..modelos.usuarios import Profesional


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

