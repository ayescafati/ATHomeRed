from __future__ import annotations
from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional
from uuid import UUID
from enum import Enum
from decimal import Decimal
from ..value_objects.objetos_valor import Dinero, Ubicacion

class EstadoConsulta(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"

@dataclass
class Consulta:
    """Entidad de agenda: una cita entre paciente y profesional."""
    id: UUID
    id_paciente: UUID
    id_profesional: Optional[int]
    fecha: date
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    ubicacion: Ubicacion
    estado: EstadoConsulta = EstadoConsulta.PENDIENTE
    monto_acordado: Optional[Dinero] = None
    id_direccion: Optional[int] = None  # dirección del encuentro (DB normaliza)

    def confirmar(self) -> None:
        if self.estado != EstadoConsulta.PENDIENTE:
            raise ValueError("Solo se pueden confirmar consultas pendientes")
        self.estado = EstadoConsulta.CONFIRMADA

    def cancelar(self) -> None:
        if self.estado == EstadoConsulta.COMPLETADA:
            raise ValueError("No se puede cancelar una consulta completada")
        self.estado = EstadoConsulta.CANCELADA

    def completar(self) -> None:
        if self.estado != EstadoConsulta.CONFIRMADA:
            raise ValueError("Solo se pueden completar consultas confirmadas")
        self.estado = EstadoConsulta.COMPLETADA

    def set_monto(self, monto: Decimal, moneda: str = "ARS") -> None:
        self.monto_acordado = Dinero(monto=monto, moneda=moneda)
