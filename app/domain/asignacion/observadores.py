# from __future__ import annotations
# from abc import ABC, abstractmethod
# from typing import List
# from ..modelos.eventos import Event


# class Observer(ABC):
#     @abstractmethod
#     def update(self, evt: Event) -> None:
#         pass


# class Subject(ABC):
#     observers: List[Observer]

#     def attach(self, obs: Observer) -> None:
#         pass

#     def detach(self, obs: Observer) -> None:
#         pass

#     def notify(self, evt: Event) -> None:
#         pass


# class NotificadorEmail(Observer):
#     def update(self, evt: Event) -> None:
#         pass


# class AuditLogger(Observer):
#     def update(self, evt: Event) -> None:
#         pass


from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from ..modelos.eventos import Event

class Observer(ABC):
    @abstractmethod
    def update(self, evt: Event) -> None:
        ...

class Subject(ABC):
    observers: List[Observer]

    def __init__(self) -> None:
        self.observers = []

    def attach(self, obs: Observer) -> None:
        if obs not in self.observers:
            self.observers.append(obs)

    def detach(self, obs: Observer) -> None:
        try:
            self.observers.remove(obs)
        except ValueError:
            pass  # si no estaba, ignoramos

    def notify(self, evt: Event) -> None:
        # fail-safe: un handler no debe frenar a los demás
        for obs in list(self.observers):
            try:
                obs.update(evt)
            except Exception as e:
                # en una versión con logging real, registraríamos este error
                print(f"[ObserverError] {obs.__class__.__name__}: {e}")

class NotificadorEmail(Observer):
    def update(self, evt: Event) -> None:
        # stub simple: en producción inyectás un EmailService
        try:
            print(f"[EMAIL] tipo={getattr(evt, 'tipo', None)} cita_id={getattr(evt, 'cita_id', None)} datos={getattr(evt, 'datos', None)}")
        except Exception:
            print("[EMAIL] evento recibido")

class AuditLogger(Observer):
    def update(self, evt: Event) -> None:
        # stub simple: en producción, escribiría en tabla log_evento o SIEM
        try:
            print(f"[AUDIT] tipo={getattr(evt, 'tipo', None)} cita_id={getattr(evt, 'cita_id', None)} datos={getattr(evt, 'datos', None)}")
        except Exception:
            print("[AUDIT] evento recibido")
