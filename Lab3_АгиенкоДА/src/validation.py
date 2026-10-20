"""Класс вычислений / валидации (логика из лабораторной работы №1).

Единственный публичный метод validate проверяет регистрационные данные:
логин (телефон / email / строка + чёрный список) и пароль (кириллица,
регистры, цифра, спецсимвол, подтверждение).
"""
import re

# --- Чёрный список запрещённых логинов ------------------------------
BLACKLIST = {
    "admin", "administrator", "root", "superuser", "moderator",
    "moder", "user", "guest", "test", "qwerty", "password", "support",
}

# --- Маски ------------------------------------------------------------
PHONE_RE = re.compile(r"^\+[0-9]-[0-9]{3}-[0-9]{3}-[0-9]{4}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
LOGIN_STR_RE = re.compile(r"^[A-Za-z0-9_]+$")

CYRILLIC_UPPER = set("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
CYRILLIC_LOWER = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
DIGITS = set("0123456789")

PASSWORD_MIN_LENGTH = 7
LOGIN_MIN_LENGTH = 5


class RegistrationValidator:
    """Класс валидации: один метод validate (по заданию ЛР1)."""

    def validate(self, login: str, password: str, confirm: str) -> tuple[bool, str]:
        """Возвращает (успех, сообщение_об_ошибке)."""
        error = self._validate_login(login)
        if error:
            return False, error

        error = self._validate_password(password, confirm)
        if error:
            return False, error

        return True, ""

    def _validate_login(self, login: str) -> str | None:
        if not login:
            return "Логин не может быть пустым"

        if login.lower() in BLACKLIST:
            return "Данный логин находится в чёрном списке и запрещён к использованию"

        if login.startswith("+"):
            if not PHONE_RE.match(login):
                return "Некорректный формат телефона: ожидается +x-xxx-xxx-xxxx"
            return None

        if "@" in login:
            if not EMAIL_RE.match(login):
                return "Некорректный формат email"
            return None

        if len(login) < LOGIN_MIN_LENGTH:
            return f"Логин слишком короткий: минимум {LOGIN_MIN_LENGTH} символов"
        if not LOGIN_STR_RE.match(login):
            return "Логин содержит недопустимые символы: только латиница, цифры и знак подчёркивания"
        return None

    def _validate_password(self, password: str, confirm: str) -> str | None:
        if not password:
            return "Пароль не может быть пустым"

        if len(password) < PASSWORD_MIN_LENGTH:
            return f"Пароль слишком короткий: минимум {PASSWORD_MIN_LENGTH} символов"

        has_upper = False
        has_lower = False
        has_digit = False
        has_special = False

        for ch in password:
            if ch in CYRILLIC_UPPER:
                has_upper = True
            elif ch in CYRILLIC_LOWER:
                has_lower = True
            elif ch in DIGITS:
                has_digit = True
            elif ch.isascii() and ch.isalpha():
                return "Пароль содержит недопустимые символы: только кириллица, цифры и спецсимволы"
            else:
                has_special = True

        if not has_upper:
            return "В пароле должна быть минимум одна буква верхнего регистра"
        if not has_lower:
            return "В пароле должна быть минимум одна буква нижнего регистра"
        if not has_digit:
            return "В пароле должна быть минимум одна цифра"
        if not has_special:
            return "В пароле должен быть минимум один спецсимвол"

        if password != confirm:
            return "Пароль и подтверждение пароля не совпадают"
        return None
