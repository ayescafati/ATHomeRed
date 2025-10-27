from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Event:
    tipo: str
    cita_id: int
    datos: Dict[str, Any]
