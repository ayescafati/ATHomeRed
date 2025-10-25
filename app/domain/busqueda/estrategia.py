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



from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Iterable
from ..modelos.catalogo import FiltroBusqueda, Publicacion
from ..modelos.usuarios import Profesional

def _match_zona(p: Profesional, filtro: FiltroBusqueda) -> bool:
    """Coincidencia por provincia/departamento/barrio si vienen en el filtro."""
    ub = getattr(p, "ubicacion", None)
    if ub is None:
        return False
    prov = getattr(filtro, "provincia", None)
    dpto = getattr(filtro, "departamento", None)
    barrio = getattr(filtro, "barrio", None)

    if prov and getattr(ub, "provincia", None) != prov:
        return False
    if dpto and getattr(ub, "departamento", None) != dpto:
        return False
    if barrio and getattr(ub, "barrio", None) != barrio:
        return False
    return True

def _match_especialidad(p: Profesional, filtro: FiltroBusqueda) -> bool:
    esp_id = getattr(filtro, "especialidad_id", None)
    if not esp_id:
        return True
    # Profesional.especialidades: List[Especialidad] con atributo id
    for e in getattr(p, "especialidades", []) or []:
        if getattr(e, "id", None) == esp_id:
            return True
    return False

def _ordenar_por_distancia(items: Iterable[Profesional], filtro: FiltroBusqueda) -> List[Profesional]:
    """Si hay ubicacion en el filtro y el profesional implementa calcular_distancia, ordena por distancia."""
    ub_ref = getattr(filtro, "ubicacion", None)
    if ub_ref is None:
        return list(items)
    def dist_or_none(prof: Profesional):
        calc = getattr(prof, "calcular_distancia", None)
        if callable(calc):
            try:
                return calc(ub_ref)
            except Exception:
                return None
        return None
    # Mantener estables: profesionales sin distancia al final
    with_dist = []
    without_dist = []
    for prof in items:
        d = dist_or_none(prof)
        (with_dist if d is not None else without_dist).append((d, prof))
    with_dist.sort(key=lambda t: t[0])  # ascendente
    return [p for _, p in with_dist] + [p for _, p in [(None, x) for x in without_dist]]

class EstrategiaBusqueda(ABC):
    @abstractmethod
    def buscar(
        self,
        filtro: FiltroBusqueda,
        profesionales: List[Profesional],
        publicaciones: List[Publicacion],
    ) -> List[Profesional]:
        ...

class BusquedaPorZona(EstrategiaBusqueda):
    def buscar(
        self,
        filtro: FiltroBusqueda,
        profesionales: List[Profesional],
        publicaciones: List[Publicacion],
    ) -> List[Profesional]:
        candidatos = [p for p in profesionales if _match_zona(p, filtro)]
        return _ordenar_por_distancia(candidatos, filtro)

class BusquedaPorEspecialidad(EstrategiaBusqueda):
    def buscar(
        self,
        filtro: FiltroBusqueda,
        profesionales: List[Profesional],
        publicaciones: List[Publicacion],
    ) -> List[Profesional]:
        return [p for p in profesionales if _match_especialidad(p, filtro)]

class BusquedaCombinada(EstrategiaBusqueda):
    def buscar(
        self,
        filtro: FiltroBusqueda,
        profesionales: List[Profesional],
        publicaciones: List[Publicacion],
    ) -> List[Profesional]:
        # Primero zona, luego especialidad, para reducir el universo
        zona = [p for p in profesionales if _match_zona(p, filtro)]
        zona_y_especialidad = [p for p in zona if _match_especialidad(p, filtro)]
        return _ordenar_por_distancia(zona_y_especialidad, filtro)
