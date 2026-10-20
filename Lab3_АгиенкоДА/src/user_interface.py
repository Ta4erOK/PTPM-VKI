"""Класс взаимодействия с пользователем (интерфейс на abc)."""
from abc import ABC, abstractmethod


class UserInterface(ABC):
    """Абстрактный интерфейс получения данных от пользователя."""

    @abstractmethod
    def get_credentials(self) -> tuple[str, str, str]:
        """Вернуть тройку (логин, пароль, подтверждение пароля)."""


class ConsoleUserInterface(UserInterface):
    """Консольный ввод через input()."""

    def get_credentials(self) -> tuple[str, str, str]:
        login = input("Логин: ").strip()
        password = input("Пароль: ").strip()
        confirm = input("Повторите пароль: ").strip()
        return login, password, confirm
