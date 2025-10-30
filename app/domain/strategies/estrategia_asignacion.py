from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.entities.agenda import Consulta
    from app.domain.entities.usuarios import Profesional

class AsignacionStrategy(ABC):
     @abstractmethod
     def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
         pass

class DisponibilidadHorariaStrategy(AsignacionStrategy):
    def validar(self, cita: "Consulta", profesional) -> bool:
        for c in profesional:
            if c.fecha == cita.fecha and c.hora_inicio == cita.hora_inicio:
                return False
        return True
    
class MatriculaProvinciaStrategy(AsignacionStrategy):
    def validar(self, cita: "Consulta", profesional) -> bool:
          return any(m.provincia == cita.ubicacion.provincia for m in profesional.matriculas)
        
# class DisponibilidadHorariaStrategy(AsignacionStrategy):
#     def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
#         pass


# class MatriculaProvinciaStrategy(AsignacionStrategy):
#     def validar(self, cita: "Consulta", profesional: "Profesional") -> bool:
#         pass

