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
        self.assertIn("телефона", validate_login("+a-999-123-4567"))  # буква

    def test_phone_without_plus_treated_as_string(self):
        # Нет '+' в начале -> обрабатывается как обычная строка, дефисы недопустимы
        self.assertIn("недопустимые символы", validate_login("7-999-123-4567"))

    def test_valid_email_accepted(self):
        self.assertIsNone(validate_login("user@example.com"))
        self.assertIsNone(validate_login("ivan.petrov@mail.ru"))

    def test_invalid_email_rejected(self):
        self.assertIn("email", validate_login("user@example"))
        self.assertIn("email", validate_login("user@@example.com"))

    def test_short_string_login_rejected(self):
        self.assertIn("короткий", validate_login("ivan"))  # 4 символа

    def test_string_login_with_forbidden_chars_rejected(self):
        self.assertIn("недопустимые символы", validate_login("ivan петров"))
        self.assertIn("недопустимые символы", validate_login("иван_2026"))  # кириллица
        self.assertIn("недопустимые символы", validate_login("ivan-2026"))

    def test_valid_string_login_accepted(self):
        self.assertIsNone(validate_login("ivan_2026"))


class TestValidatePassword(unittest.TestCase):
    def test_valid_password_accepted(self):
        self.assertIsNone(validate_password(VALID_PASSWORD, VALID_CONFIRM))

    def test_empty_password_rejected(self):
        self.assertEqual(validate_password("", ""), "Пароль не может быть пустым")

    def test_short_password_rejected(self):
        self.assertIn("короткий", validate_password("Пар1!", "Пар1!"))
        self.assertIn("короткий", validate_password("аБв1!а", "аБв1!а"))

    def test_password_with_latin_letters_rejected(self):
        self.assertIn("недопустимые символы", validate_password("Password1!", "Password1!"))

    def test_password_without_upper_letter_rejected(self):
        self.assertIn("верхнего регистра", validate_password("пароль1!", "пароль1!"))

    def test_password_without_lower_letter_rejected(self):
        self.assertIn("нижнего регистра", validate_password("ПАРОЛЬ1!", "ПАРОЛЬ1!"))

    def test_password_without_digit_rejected(self):
        self.assertIn("цифра", validate_password("Пароль!!", "Пароль!!"))

    def test_password_without_special_symbol_rejected(self):
        self.assertIn("спецсимвол", validate_password("Пароль11", "Пароль11"))

    def test_password_mismatch_rejected(self):
        self.assertIn("не совпадают", validate_password(VALID_PASSWORD, "Другой1!"))


class TestValidateRegistration(unittest.TestCase):
    def test_success_registration_string_login(self):
        self.assertEqual(validate_registration("ivan_2026", VALID_PASSWORD, VALID_CONFIRM), (True, ""))

    def test_success_registration_phone_login(self):
        self.assertEqual(validate_registration("+7-999-123-4567", VALID_PASSWORD, VALID_CONFIRM), (True, ""))

    def test_success_registration_email_login(self):
        self.assertEqual(validate_registration("ivan@example.com", VALID_PASSWORD, VALID_CONFIRM), (True, ""))

    def test_failure_registration_wrong_login(self):
        result, message = validate_registration("", VALID_PASSWORD, VALID_CONFIRM)
        self.assertFalse(result)

    def test_failure_registration_wrong_password(self):
        result, message = validate_registration("ivan_2026", "пароль1!", "пароль1!")
        self.assertFalse(result)
        self.assertNotEqual(message, "")


class TestMaskPassword(unittest.TestCase):
    def test_same_password_gets_same_hash(self):
        self.assertEqual(mask_password(VALID_PASSWORD), mask_password(VALID_PASSWORD))

    def test_different_passwords_get_different_hashes(self):
        self.assertNotEqual(mask_password("Пароль1!"), mask_password("Пароль2!"))

    def test_hash_is_sha256_hex_of_64_chars(self):
        self.assertEqual(len(mask_password(VALID_PASSWORD)), 64)
        self.assertTrue(mask_password(VALID_PASSWORD).isalnum())

    def test_plain_password_not_contained_in_hash(self):
        self.assertNotIn(VALID_PASSWORD, mask_password(VALID_PASSWORD))


if __name__ == "__main__":
    unittest.main()