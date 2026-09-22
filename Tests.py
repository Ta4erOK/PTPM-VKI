"""Модульные тесты для лабораторной работы №1, Вариант 2.

Покрывают: валидацию логина (телефон/email/строка), чёрный список,
все правила пароля, совпадение паролей и маскирование.
"""
import unittest

from validation import (
    BLACKLIST,
    validate_login,
    validate_password,
    validate_registration,
    mask_password,
)


# Валидные данные, которые можно переиспользовать
VALID_PASSWORD = "Пароль1!"  # кириллица в верхнем/нижнем регистре, цифра, спецсимвол
VALID_CONFIRM = VALID_PASSWORD


class TestValidateLogin(unittest.TestCase):
    def test_empty_login(self):
        self.assertEqual(validate_login(""), "Логин не может быть пустым")

    def test_blacklist(self):
        for banned in BLACKLIST:
            self.assertEqual(
                validate_login(banned),
                "Данный логин находится в чёрном списке и запрещён к использованию",
                msg=f"login={banned!r}",
            )

    def test_valid_phone(self):
        self.assertIsNone(validate_login("+7-999-123-4567"))

    def test_invalid_phone(self):
        self.assertIn("телефона", validate_login("+79991234567"))  # без дефисов
        self.assertIn("недопустимые символы", validate_login("7-999-123-4567"))  # без + -> трактуется как строка
        self.assertIn("телефона", validate_login("+7-999-123456"))  # не та длина
        self.assertIn("телефона", validate_login("+a-999-123-4567"))  # буква вместо цифры

    def test_valid_email(self):
        self.assertIsNone(validate_login("user@example.com"))
        self.assertIsNone(validate_login("ivan.petrov@mail.ru"))
        self.assertIsNone(validate_login("test_1@sub.domain.org"))

    def test_invalid_email(self):
        self.assertIn("email", validate_login("user@example"))
        self.assertIn("email", validate_login("user@@example.com"))
        self.assertIn("email", validate_login("@example.com"))
        self.assertIn("email", validate_login("user@.com"))

    def test_valid_string_login(self):
        self.assertIsNone(validate_login("ivan_2026"))

    def test_short_string_login(self):
        self.assertIn("короткий", validate_login("ivan"))  # 4 символа

    def test_invalid_chars_in_string_login(self):
        self.assertIn("недопустимые символы", validate_login("ivan петров"))
        self.assertIn("недопустимые символы", validate_login("ivan-2026"))
        self.assertIn("недопустимые символы", validate_login("иван_2026"))  # кириллица


class TestValidatePassword(unittest.TestCase):
    def test_valid_password(self):
        self.assertIsNone(validate_password(VALID_PASSWORD, VALID_CONFIRM))

    def test_empty_password(self):
        self.assertEqual(validate_password("", ""), "Пароль не может быть пустым")

    def test_short_password(self):
        self.assertIn("короткий", validate_password("Пар1!", "Пар1!"))  # 5 символов
        # 6 символов для контроля границы (минимум 7)
        self.assertIn("короткий", validate_password("аБв1!а", "аБв1!а"))

    def test_latin_letters_forbidden(self):
        self.assertIn("недопустимые символы", validate_password("Password1!", "Password1!"))

    def test_requires_upper_letter(self):
        self.assertIn("верхнего регистра", validate_password("пароль1!", "пароль1!"))

    def test_requires_lower_letter(self):
        self.assertIn("нижнего регистра", validate_password("ПАРОЛЬ1!", "ПАРОЛЬ1!"))

    def test_requires_digit(self):
        self.assertIn("цифра", validate_password("Пароль!!", "Пароль!!"))

    def test_requires_special_symbol(self):
        self.assertIn("спецсимвол", validate_password("Пароль11", "Пароль11"))

    def test_password_mismatch(self):
        self.assertIn("не совпадают", validate_password(VALID_PASSWORD, "Другой1!"))


class TestValidateRegistration(unittest.TestCase):
    def test_success(self):
        self.assertEqual(validate_registration("ivan_2026", VALID_PASSWORD, VALID_CONFIRM), (True, ""))

    def test_success_phone(self):
        self.assertEqual(validate_registration("+7-999-123-4567", VALID_PASSWORD, VALID_CONFIRM), (True, ""))

    def test_success_email(self):
        self.assertEqual(validate_registration("ivan@example.com", VALID_PASSWORD, VALID_CONFIRM), (True, ""))

    def test_fail_login(self):
        result, message = validate_registration("", VALID_PASSWORD, VALID_CONFIRM)
        self.assertFalse(result)
        self.assertEqual(message, "Логин не может быть пустым")

    def test_fail_password(self):
        result, message = validate_registration("ivan_2026", "пароль1!", "пароль1!")
        self.assertFalse(result)
        self.assertIn("верхнего регистра", message)


class TestMaskPassword(unittest.TestCase):
    def test_same_password_same_hash(self):
        self.assertEqual(mask_password(VALID_PASSWORD), mask_password(VALID_PASSWORD))

    def test_different_passwords_different_hashes(self):
        self.assertNotEqual(mask_password("Пароль1!"), mask_password("Пароль2!"))

    def test_hash_is_sha256_hex(self):
        self.assertEqual(len(mask_password(VALID_PASSWORD)), 64)
        self.assertTrue(mask_password(VALID_PASSWORD).isalnum())

    def test_plain_password_not_in_hash(self):
        self.assertNotIn(VALID_PASSWORD, mask_password(VALID_PASSWORD))


if __name__ == "__main__":
    unittest.main()