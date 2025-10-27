from __future__ import annotations
import datetime as dt
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from ..value_objects.objetos_valor import Ubicacion, Disponibilidad, Matricula
from .catalogo import Especialidad

@dataclass
class Usuario(ABC):
    id: UUID
    nombre: str
    apellido: str
    email: str
    celular: str
    ubicacion: Ubicacion
    activo: bool = True

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}".strip()

    def activar(self) -> None: self.activo = True
    def desactivar(self) -> None: self.activo = False
    def datos_contacto(self) -> str:
        return f"{self.nombre_completo} <{self.email}> ({self.celular or 's/teléfono'})"

@dataclass
class Profesional(Usuario):
    verificado: bool = False
    especialidades: List[Especialidad] = field(default_factory=list)
    disponibilidades: List[Disponibilidad] = field(default_factory=list)
    matriculas: List[Matricula] = field(default_factory=list)

    def agregar_disponibilidad(self, d: Disponibilidad) -> None:
        self.disponibilidades.append(d)

@dataclass
class Responsable(Usuario):
    pacientes: List["Paciente"] = field(default_factory=list)
    relacion_con_paciente: str = ""

@dataclass
class Paciente(Usuario):
    fecha_nacimiento: dt.date = field(default_factory=lambda: dt.date(2000, 1, 1))
    cobertura: str = ""
    notas: str = ""

    def edad(self, hoy: Optional[dt.date] = None) -> int:
        hoy = hoy or dt.date.today()
        years = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            years -= 1
        return years

    def datos_contacto(self) -> str:
        return f"{self.nombre_completo} <{self.email}> ({self.celular or 's/teléfono'})"
