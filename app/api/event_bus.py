"""
Event Bus: Sistema centralizado de publicación de eventos.

Desacopla el dominio de los observadores. Los eventos se publican
desde los routers y los observadores se suscriben sin que el dominio
lo sepa.
"""

from app.domain.observers.observadores import EventBus, NotificadorEmail

# Instancia global del bus de eventos
event_bus = EventBus()

# Crear observadores y suscribirlos a todos los eventos de cita
notificador_email = NotificadorEmail()

# Eventos que disparan notificaciones
_EVENTOS_NOTIFICABLES = [
    "cita.creada",
    "cita.confirmada",
    "cita.cancelada",
    "cita.reprogramada",
    "cita.completada",
]

for evento in _EVENTOS_NOTIFICABLES:
    event_bus.suscribir_observer(evento, notificador_email)


def get_event_bus() -> EventBus:
    """Dependency injection para obtener el event bus"""
    return event_bus
