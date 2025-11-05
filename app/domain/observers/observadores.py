"""Infra mínima del patrón Observer/Subject en la capa de dominio.

Acá definimos:
- Observer: interfaz abstracta que cualquier “suscriptor” tiene que implementar.
- Subject: el publicador/observable que mantiene una lista de observers y los notifica.
- Implementaciones de ejemplo (NotificadorEmail, AuditLogger) a modo placeholder.

Cuando sucede un Event de dominio, el Subject avisa a todos los
observers sin acoplarse a sus detalles. Si uno falla, no tiramos todo abajo.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.domain.eventos import Event


class Observer(ABC):
    """Contrato para quien quiera enterarse de eventos de dominio."""

    @abstractmethod
    def update(self, evt: Event) -> None:
        """Recibe la notificación de un evento y actúa en consecuencia."""
        raise NotImplementedError


class Subject:
    """Implementación liviana del patrón Subject (Observable).

    Mantiene y gestiona la lista de observers, y los notifica ante cada evento.
    """

    def __init__(self) -> None:
        # Lista interna de suscriptores; evitamos exponerla para no romper invariantes.
        self._observers: List[Observer] = []

    def attach(self, obs: Observer) -> None:
        """Se suscribe un observer (sin duplicados)."""
        if obs not in self._observers:
            self._observers.append(obs)

    def detach(self, obs: Observer) -> None:
        """Se desuscribe un observer si estaba registrado."""
        if obs in self._observers:
            self._observers.remove(obs)

    def notify(self, evt: Event) -> None:
        """Notifica a todos los observers.

        Cada `update` va en un try/except para que una falla no corte la cadena.
        Copiamos la lista (`list(self._observers)`) por si alguien subscribe/desuscribe
        en medio de la iteración (defensa simple contra modificaciones concurrentes).
        """
        for obs in list(self._observers):
            try:
                obs.update(evt)
            except Exception:
                # En una app real conviene loggear/monitorizar el error en vez de silenciarlo.
                # Ej: logger.exception("Fallo notificando observer %r con evento %r", obs, evt)
                pass


class NotificadorEmail(Observer):
    """Observer de ejemplo: “enviaría” un mail ante cada evento."""

    def update(self, evt: Event) -> None:
        # Placeholder: acá iría la integración real (cola de tareas, SMTP, proveedor, etc.).
        # print(f"[EMAIL] Evento: {evt.tipo} datos={evt.datos}")
        pass


class AuditLogger(Observer):
    """Observer de ejemplo: registraría el evento en auditoría/logs."""

    def update(self, evt: Event) -> None:
        # Placeholder: persistir auditoría, enviar a un sink de logs, SIEM, etc.
        # print(f"[AUDIT] Evento: {evt.tipo}")
        pass
