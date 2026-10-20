"""Класс-контроллер: сквозной сценарий регистрации.

1. Запросить данные у пользователя (класс взаимодействия).
2. Если записи нет в БД — проверить данные (класс валидации) и сохранить
   результат; если запись есть — взять результат из БД (кэш).
3. Отправить строку-результат сторонней зависимости.
4. Вернуть строку-результат.
"""
from db import RegistrationRepository
from external_dependency import ExternalDependency
from user_interface import UserInterface
from validation import RegistrationValidator


class RegistrationController:
    """Бизнес-логика сквозного сценария регистрации."""

    def __init__(
        self,
        validator: RegistrationValidator,
        repository: RegistrationRepository,
        user_interface: UserInterface,
        external: ExternalDependency,
    ) -> None:
        self._validator = validator
        self._repository = repository
        self._user_interface = user_interface
        self._external = external

    def run(self) -> str:
        """Выполнить сценарий и вернуть строку-результат."""
        # 1. Входные данные от пользователя
        login, password, confirm = self._user_interface.get_credentials()

        # 2. Проверка наличия записи в БД
        record = self._repository.get(login, password, confirm)
        if record is None:
            # Нет записи -> вычисляем результат и сохраняем в БД
            result, error = self._validator.validate(login, password, confirm)
            self._repository.add(login, password, confirm, result, error)
        else:
            # Запись есть -> результат берётся из БД
            result, error = record["result"], record["error"]

        # 3. Строка-результата уходит сторонней зависимости
        if result:
            message = f"Регистрация {login}: выполнена успешно"
        else:
            message = f"Регистрация {login}: отклонена — {error}"
        self._external.send(message)

        # 4. Результат операции наружу
        return message
