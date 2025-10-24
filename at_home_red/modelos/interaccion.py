from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import List, TYPE_CHECKING
from uuid import UUID

from ..enumeraciones import EstadoCita
from ..asignacion.observadores import Subject, Observer
from .eventos import Event

if TYPE_CHECKING:
    from ..asignacion.estrategia_asignacion import AsignacionStrategy
    from .usuarios import Profesional, Paciente


@dataclass
class Consulta(Subject):
    id: UUID
    paciente: "Paciente"
    profesional: "Profesional"
    fecha: datetime.date
    hora_inicio: datetime.time
    hora_fin: datetime.time
    estado: EstadoCita
    notas: str
    observers: List[Observer] = field(default_factory=list)

    def solicitar(self) -> None:
        pass

    def confirmar(self) -> None:
        pass

    def cancelar(self, motivo: str) -> None:
        pass

    def reprogramar(
        self, nueva_fecha: date, nueva_hora_inicio: time, nueva_hora_fin: time
    ) -> None:
        pass

    def cambiar_estado(self, nuevo: EstadoCita) -> None:
        pass

    def duracion_min(self) -> int:
        pass

    def solapa_con(self, otra: "Consulta") -> bool:
        pass

    def asignar(
        self, prof: "Profesional", strategy: "AsignacionStrategy"
    ) -> bool:
        pass

    def attach(self, obs: Observer) -> None:
        pass

    def detach(self, obs: Observer) -> None:
        pass

    def notify(self, evt: "Event") -> None:
        pass
