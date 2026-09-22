"""Лабораторная работа №1, Вариант 2.

Проверка данных пользователя при регистрации.
Сквозное логирование всех ключевых событий в консоль и файл.
"""
import logging

from logger_config import setup_logger
from validation import mask_password, validate_registration


def main():
    # Настройка логгера должна быть самой первой операцией программы
    setup_logger()

    print("Регистрация пользователя (q — выход)")

    while True:
        login = input("Введите логин (телефон / email / строка): ").strip()
        if login.lower() == "q":
            logging.info("Пользователь завершил работу программы")
            break

        password = input("Введите пароль: ")
        confirm = input("Подтвердите пароль: ")

        # Пароли маскируются ДО логирования — в открытом виде их нигде нет
        pass_hash = mask_password(password)
        confirm_hash = mask_password(confirm)

        try:
            result, message = validate_registration(login, password, confirm)
        except Exception:
            # Непредвиденный сбой: логируем с полной трассировкой стека
            logging.exception(
                "Непредвиденная ошибка при валидации | "
                f"login={login!r} | password_hash={pass_hash}"
            )
            result, message = False, "Непредвиденная ошибка при валидации"

        if result:
            logging.info(
                "Успешная регистрация | "
                f"login={login!r} | password_hash={pass_hash} | "
                f"confirm_hash={confirm_hash} | результат=True"
            )
            print("True")
            print()
        else:
            logging.error(
                "Регистрация отклонена | "
                f"login={login!r} | password_hash={pass_hash} | "
                f"confirm_hash={confirm_hash} | результат=False | причина: {message}"
            )
            print("False")
            print(message)
            print()


if __name__ == "__main__":
    main()