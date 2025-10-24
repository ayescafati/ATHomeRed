from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import List, TYPE_CHECKING

from ..enumeraciones import DiaSemana

if TYPE_CHECKING:
    from .usuarios import Profesional


@dataclass
class Disponibilidad:
    dias_semana: List["DiaSemana"]
    hora_inicio: time
    hora_fin: time

    def mostrar_disponibilidad(self) -> None:
        pass

    def esta_disponible(self, fecha: date, hora: time) -> bool:
        pass


@dataclass
class Especialidad:
    id_especialidad: int
    nombre: str
    categoria: str
    descripcion: str
    tarifa: float

    def mostrar_detalles(self) -> None:
        pass


@dataclass
class Publicacion:
    profesional: "Profesional"
    titulo: str
    descripcion: str
    especialidad: "Especialidad"
    fecha_publicacion: date

    def mostrar_detalles(self) -> None:
        pass

    def es_visible(self) -> bool:
        pass


@dataclass
class FiltroBusqueda:
    especialidad: str
    zona: str
    rango_horario: str
