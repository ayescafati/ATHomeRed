from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from ..modelos.eventos import Event

class Observer(ABC):
    @abstractmethod
    def update(self, evt: Event) -> None: pass

class Subject(ABC):
    observers: List[Observer]
    def attach(self, obs: Observer) -> None: pass
    def detach(self, obs: Observer) -> None: pass
    def notify(self, evt: Event) -> None: pass

class NotificadorEmail(Observer):
    def update(self, evt: Event) -> None: pass

class AuditLogger(Observer):
    def update(self, evt: Event) -> None: pass
