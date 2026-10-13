"""Тесты для собственного проекта из Лабораторной работы №1.

Проект: валидация учётных данных при регистрации (my_project.py).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from my_project import (
    BLACKLIST,
    validate_login,
    validate_password,
    validate_registration,
    mask_password,
)


# Валидные данные
VALID_PASSWORD = "Пароль1!"  # кириллица, регистры, цифра, спецсимвол
VALID_CONFIRM = VALID_PASSWORD
VALID_LOGIN = "ivan_2026"


class TestValidateLogin(unittest.TestCase):
    def test_empty_login_returns_error(self):
        self.assertEqual(validate_login(""), "Логин не может быть пустым")

    def test_blacklisted_login_returns_error(self):
        for banned in BLACKLIST:
            self.assertEqual(
                validate_login(banned),
                "Данный логин находится в чёрном списке и запрещён к использованию",
                msg=f"login={banned!r}",
            )

    def test_valid_phone_accepted(self):
        self.assertIsNone(validate_login("+7-999-123-4567"))

    def test_invalid_phone_rejected(self):
        self.assertIn("телефона", validate_login("+79991234567"))  # без дефисов

    def test_valid_email_accepted(self):
        self.assertIsNone(validate_login("user@example.com"))
        self.assertIsNone(validate_login("ivan.petrov@mail.ru"))

    def test_valid_string_login_accepted(self):
        self.assertIsNone(validate_login("ivan_2026"))


class TestValidatePassword(unittest.TestCase):
    def test_valid_password_accepted(self):
        self.assertIsNone(validate_password(VALID_PASSWORD, VALID_CONFIRM))

    def test_short_password_rejected(self):
        self.assertIn("короткий", validate_password("Пар1!", "Пар1!"))


class TestValidateRegistration(unittest.TestCase):
    def test_success_registration_string_login(self):
        self.assertEqual(validate_registration("ivan_2026", VALID_PASSWORD, VALID_CONFIRM), (True, ""))


class TestMaskPassword(unittest.TestCase):
    def test_hash_is_sha256_hex_of_64_chars(self):
        self.assertEqual(len(mask_password(VALID_PASSWORD)), 64)
        self.assertTrue(mask_password(VALID_PASSWORD).isalnum())


if __name__ == "__main__":
    unittest.main()