"""Класс сторонней зависимости (интерфейс на abc).

Реализация имитирует передачу данных на внешний email-сервер:
без реальной сети — только фиксация отправленного.
"""
from abc import ABC, abstractmethod


class ExternalDependency(ABC):
    """Абстрактный интерфейс сторонней зависимости."""

    @abstractmethod
    def send(self, payload: str) -> bool:
        """Передать строку-результат внешнему процессу."""


class EmailServerStub(ExternalDependency):
    """Имитация email-сервера: отправки в сеть нет, всё пишется в журнал."""

    def __init__(self) -> None:
        self.outbox: list[str] = []

    def send(self, payload: str) -> bool:
        # Чистая имитация: данные «уходят» только в локальный журнал
        self.outbox.append(payload)
        return True
