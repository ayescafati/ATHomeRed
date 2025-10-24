from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Ubicacion:
    calle: str
    numero: str
    barrio: str
    ciudad: str
    provincia: str
    latitud: float
    longitud: float

    def __str__(self) -> str:
        pass

    def distancia_a(self, otra: "Ubicacion") -> float:
        pass

    def pertenece_a_zona(self, zona: str) -> bool:
        pass

    def es_valida(self) -> bool:
        pass
