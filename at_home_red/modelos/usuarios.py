import datetime
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from .objetos_valor import Ubicacion
from usuarios import Profesional, Paciente
from .catalogo import Especialidad, Disponibilidad, FiltroBusqueda, Publicacion
from interaccion import Consulta

@dataclass
class Usuario(ABC):
    id: UUID
    nombre: str
    apellido: str
    email: str
    celular: str
    ubicacion: Ubicacion
    activo: bool
    def activar(self) -> None: pass
    def desactivar(self) -> None: pass
    def datos_contacto(self) -> str: pass

@dataclass
class Profesional(Usuario):
    verificado: bool
    matricula: str
    especialidades: List["Especialidad"] = field(default_factory=list)
    def publicar(self) -> None: pass
    def agregar_disponibilidad(self, d: "Disponibilidad") -> None: pass
    def mostrar_perfil(self) -> None: pass
    def calcular_distancia(self, a: Ubicacion) -> float: pass

@dataclass
class Responsable(Usuario):
    pacientes: List["Paciente"] = field(default_factory=list)
    relacion_con_paciente: str = ""
    def ver_publicaciones(self, f: "FiltroBusqueda") -> List["Publicacion"]: pass
    def contactar_profesional(self, p: Profesional, msg: str, paciente: Optional["Paciente"]=None) -> "Consulta": pass

@dataclass
class Paciente:
    id: UUID
    nombre: str
    apellido: str
    fecha_nacimiento: "datetime.date"
    cobertura: str
    notas: str
    ubicacion: Ubicacion
    def edad(self) -> int: pass
