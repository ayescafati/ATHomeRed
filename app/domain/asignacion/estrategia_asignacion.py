# from __future__ import annotations

# from abc import ABC, abstractmethod
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from ..modelos.interaccion import Consulta
#     from ..modelos.usuarios import Profesional


# class AsignacionStrategy(ABC):
#     @abstractmethod
#     def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
#         pass


# class DisponibilidadHorariaStrategy(AsignacionStrategy):
#     def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
#         pass


# class MatriculaProvinciaStrategy(AsignacionStrategy):
#     def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
#         pass


from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable, Any, Optional

if TYPE_CHECKING:
    from ..modelos.interaccion import Consulta
    from ..modelos.usuarios import Profesional
    from ..modelos.objetos_valor import Disponibilidad, Matricula

class AsignacionStrategy(ABC):
    @abstractmethod
    def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
        ...

# ----------------- helpers defensivos -----------------

def _dia_coincide(dispon: "Disponibilidad", fecha) -> bool:
    """
    Acepta que DiaSemana pueda ser enum (con .value) o int.
    date.weekday(): lunes=0,...,domingo=6. Ajustamos si tu enum usa otro rango.
    """
    try:
        wd = fecha.weekday()  # 0..6
    except Exception:
        return False

    dias = getattr(dispon, "dias_semana", []) or []
    for d in dias:
        # soporta enum, int o lo que provea tu implementación
        val = getattr(d, "value", d)
        if val == wd or val == wd + 1 or val == wd - 1:
            # el == wd cubre enums 0..6; los otros dos toleran enums 1..7 (si usás lunes=1)
            return True
    return False

def _rango_horario_valido(dispon: "Disponibilidad", inicio, fin) -> bool:
    try:
        return (inicio >= dispon.hora_inicio) and (fin <= dispon.hora_fin)
    except Exception:
        return False

def _provincia_de_cita(cita: "Consulta") -> Optional[str]:
    """
    Busca provincia en distintos lugares comunes:
    cita.ubicacion.provincia  |  cita.direccion.ubicacion.provincia  |  cita.direccion.provincia
    """
    ub = getattr(cita, "ubicacion", None)
    if ub and getattr(ub, "provincia", None):
        return ub.provincia
    dir_ = getattr(cita, "direccion", None)
    if dir_:
        ub2 = getattr(dir_, "ubicacion", None)
        if ub2 and getattr(ub2, "provincia", None):
            return ub2.provincia
        if getattr(dir_, "provincia", None):
            return dir_.provincia
    return None

def _matriculas(prof: "Profesional") -> Iterable["Matricula"]:
    mats = getattr(prof, "matriculas", None)
    return mats or []

# ----------------- estrategias -----------------

class DisponibilidadHorariaStrategy(AsignacionStrategy):
    """
    Valida que la cita caiga en algún bloque de disponibilidad del profesional,
    tanto por día de semana como por rango horario.
    """
    def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
        disponibilidades: Iterable["Disponibilidad"] = getattr(profesional, "disponibilidades", []) or []
        fecha = getattr(cita, "fecha", None)
        h_ini = getattr(cita, "hora_inicio", None)
        h_fin = getattr(cita, "hora_fin", None)
        if not (fecha and h_ini and h_fin):
            return False

        for d in disponibilidades:
            if _dia_coincide(d, fecha) and _rango_horario_valido(d, h_ini, h_fin):
                return True
        return False

class MatriculaProvinciaStrategy(AsignacionStrategy):
    """
    Valida que exista una matrícula vigente del profesional en la misma provincia de la cita,
    evaluada en la fecha de la cita.
    """
    def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
        prov_cita = _provincia_de_cita(cita)
        fecha = getattr(cita, "fecha", None)
        if not (prov_cita and fecha):
            return False

        for m in _matriculas(profesional):
            try:
                misma_prov = getattr(m, "provincia", None) == prov_cita
                vigente = bool(m.esta_vigente_en(fecha))
            except Exception:
                misma_prov = False
                vigente = False
            if misma_prov and vigente:
                return True
        return False
