"""Тесты лабораторной работы №3: интеграционное тестирование и заглушки.

Интеграционные тесты (4 шт.) проверяют сквозной сценарий Controller:
ввод -> валидация -> БД -> сторонняя зависимость.
Юнит-тесты (4 шт.) проверяют новые модули (БД, имитация внешнего сервера,
консольный ввод) и НЕ дублируют проверки правил из ЛР2: правила
прогоняются через Controller, а проверяется поведение сценария
(запись в БД + отправленное сообщение), а не тексты ошибок.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from controller import RegistrationController
from db import RegistrationRepository
from external_dependency import EmailServerStub
from user_interface import ConsoleUserInterface
from validation import RegistrationValidator

VALID_LOGIN = "ivan_2026"
VALID_PASSWORD = "Пароль1!"
INVALID_LOGIN = "ab"  # короче минимума (5) -> ошибка валидации


def build_controller(db_path=":memory:", external=None):
    """Собрать контроллер с реальными БД/валидацией/вводом и переданной внешней зависимостью."""
    repository = RegistrationRepository(db_path)
    external = external if external is not None else EmailServerStub()
    controller = RegistrationController(
        validator=RegistrationValidator(),
        repository=repository,
        user_interface=ConsoleUserInterface(),
        external=external,
    )
    return controller, repository, external


class TestIntegrationController(unittest.TestCase):
    """Интеграционные тесты: полный сценарий через Controller."""

    def test_first_run_sends_result_and_stores_record(self):
        """Нет записи в БД -> валидация, сохранение, отправка внешней зависимости."""
        external = EmailServerStub()
        controller, repository, _ = build_controller(external=external)

        with patch("builtins.input", side_effect=[VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD]):
            message = controller.run()

        record = repository.get(VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD)
        self.assertIsNotNone(record)
        self.assertTrue(record["result"])
        self.assertIn("выполнена успешно", message)
        self.assertEqual(external.outbox, [message])
        repository.close()

    def test_second_run_takes_result_from_db_without_revalidation(self):
        """Есть запись в БД -> результат из БД, валидатор НЕ вызывается."""
        external = Mock()
        controller, repository, _ = build_controller(external=external)

        # Первый прогон: запись появляется в БД
        with patch("builtins.input", side_effect=[VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD]):
            first_message = controller.run()

        # Второй прогон: подменяем валидатор — если его вызовут, тест упадёт
        controller._validator = Mock(
            side_effect=AssertionError("валидатор не должен вызываться при наличии записи в БД")
        )

        with patch("builtins.input", side_effect=[VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD]):
            second_message = controller.run()

        self.assertEqual(first_message, second_message)
        external.send.assert_called_with(second_message)
        # Запись в БД осталась одна, дублей нет
        count = repository._conn.execute("SELECT COUNT(*) FROM registrations").fetchone()[0]
        self.assertEqual(count, 1)
        repository.close()

    def test_invalid_data_stored_with_error_and_message_sent(self):
        """Невалидные данные -> запись с ошибкой в БД, уходит сообщение об отклонении."""
        external = EmailServerStub()
        controller, repository, _ = build_controller(external=external)

        with patch("builtins.input", side_effect=[INVALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD]):
            message = controller.run()

        record = repository.get(INVALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD)
        self.assertIsNotNone(record)
        self.assertFalse(record["result"])
        self.assertIn("короткий", record["error"])
        self.assertIn("отклонена", message)
        self.assertEqual(external.outbox, [message])
        repository.close()

    def test_all_validation_rules_reached_through_controller(self):
        """Все правила валидации прогоняются сквозным сценарием.

        Проверяется не текст ошибки (это проверено в ЛР2), а поведение
        сценария: отказ -> запись в БД с result=0 и непустой ошибкой,
        успех -> запись с result=1. Нужно для полного покрытия проекта.
        """
        external = EmailServerStub()
        controller, repository, _ = build_controller(external=external)

        invalid_logins = [
            ("", "пустой логин"),
            ("admin", "чёрный список"),
            ("+79991234567", "телефон без дефисов"),
            ("+a-999-123-4567", "телефон с буквой"),
            ("user@example", "неполный email"),
            ("user@@example.com", "двойное @"),
            ("ab", "короткий логин"),
            ("ivan петров", "пробел в логине"),
            ("иван_2026", "кириллица в логине"),
            ("ivan-2026", "дефис в логине"),
        ]
        for login, case in invalid_logins:
            with self.subTest(case=case):
                with patch("builtins.input", side_effect=[login, VALID_PASSWORD, VALID_PASSWORD]):
                    message = controller.run()
                record = repository.get(login, VALID_PASSWORD, VALID_PASSWORD)
                self.assertIsNotNone(record, msg=case)
                self.assertFalse(record["result"], msg=case)
                self.assertTrue(record["error"], msg=case)
                self.assertIn("отклонена", message, msg=case)

        invalid_passwords = [
            ("", "пустой пароль"),
            ("аБв1!а", "короткий пароль"),
            ("Password1!", "латиница в пароле"),
            ("пароль1!", "нет верхнего регистра"),
            ("ПАРОЛЬ1!", "нет нижнего регистра"),
            ("Пароль!!", "нет цифры"),
            ("Пароль11", "нет спецсимвола"),
        ]
        for password, case in invalid_passwords:
            with self.subTest(case=case):
                with patch("builtins.input", side_effect=[VALID_LOGIN, password, password]):
                    message = controller.run()
                record = repository.get(VALID_LOGIN, password, password)
                self.assertIsNotNone(record, msg=case)
                self.assertFalse(record["result"], msg=case)
                self.assertTrue(record["error"], msg=case)
                self.assertIn("отклонена", message, msg=case)

        # Пароль и подтверждение не совпадают
        with patch("builtins.input", side_effect=[VALID_LOGIN, VALID_PASSWORD, "Другой1!"]):
            message = controller.run()
        record = repository.get(VALID_LOGIN, VALID_PASSWORD, "Другой1!")
        self.assertFalse(record["result"])
        self.assertTrue(record["error"])
        self.assertIn("отклонена", message)

        # Успешные ветки: все три типа логина
        for login in (VALID_LOGIN, "+7-999-123-4567", "user@example.com"):
            with self.subTest(login=login):
                with patch("builtins.input", side_effect=[login, VALID_PASSWORD, VALID_PASSWORD]):
                    message = controller.run()
                record = repository.get(login, VALID_PASSWORD, VALID_PASSWORD)
                self.assertTrue(record["result"])
                self.assertEqual(record["error"], "")
                self.assertIn("выполнена успешно", message)

        # Всё, что ушло наружу, — по одному сообщению на каждый запуск
        self.assertEqual(len(external.outbox), len(invalid_logins) + len(invalid_passwords) + 4)
        repository.close()


class TestDatabase(unittest.TestCase):
    """Юнит-тесты класса работы с БД (новый модуль, не из ЛР2)."""

    def setUp(self):
        self.repository = RegistrationRepository(":memory:")

    def tearDown(self):
        self.repository.close()

    def test_add_get_delete_roundtrip(self):
        self.repository.add(VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD, True, "")
        record = self.repository.get(VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(record["login"], VALID_LOGIN)
        self.assertTrue(record["result"])

        deleted = self.repository.delete(VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD)
        self.assertTrue(deleted)
        self.assertIsNone(self.repository.get(VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD))

    def test_get_returns_none_for_unknown_record(self):
        self.assertIsNone(
            self.repository.get("unknown", VALID_PASSWORD, VALID_PASSWORD)
        )


class TestExternalDependency(unittest.TestCase):
    """Юнит-тесты имитации сторонней зависимости."""

    def test_stub_keeps_sent_payload_in_outbox(self):
        stub = EmailServerStub()
        self.assertTrue(stub.send("Регистрация test: выполнена успешно"))
        self.assertEqual(stub.outbox, ["Регистрация test: выполнена успешно"])
        self.assertEqual(stub.send("сообщение 2"), True)
        self.assertEqual(len(stub.outbox), 2)


class TestUserInterface(unittest.TestCase):
    """Юнит-тесты консольного ввода с заглушкой input()."""

    def test_console_interface_returns_stripped_triple(self):
        with patch("builtins.input", side_effect=[" ivan_2026 ", "Пароль1!", "Пароль1!"]):
            credentials = ConsoleUserInterface().get_credentials()
        self.assertEqual(credentials, (VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()  # pragma: no cover
