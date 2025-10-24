from __future__ import annotations
from abc import ABC, abstractmethod
from ..modelos.interaccion import Consulta
from ..modelos.usuarios import Profesional

class AsignacionStrategy(ABC):
    @abstractmethod
    def validar(self, cita: Consulta, profesional: Profesional) -> bool: pass

class DisponibilidadHorariaStrategy(AsignacionStrategy):
    def validar(self, cita: Consulta, profesional: Profesional) -> bool: pass

class MatriculaProvinciaStrategy(AsignacionStrategy):
    def validar(self, cita: Consulta, profesional: Profesional) -> bool: pass
