"""Класс работы с базой данных (SQLite).

Запись проекта «Регистрация»: логин, пароль, подтверждение_пароля,
результат_авторизации, сообщение_об_ошибке.
Идентификатор записи — тройка (логин, пароль, подтверждение).
"""
import sqlite3


class RegistrationRepository:
    """CRUD-операции над таблицей registrations."""

    def __init__(self, db_path: str = ":memory:"):
        # ":memory:" — база в памяти,
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                login    TEXT NOT NULL,
                password TEXT NOT NULL,
                confirm  TEXT NOT NULL,
                result   INTEGER NOT NULL,
                error    TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (login, password, confirm)
            )
            """
        )
        self._conn.commit()

    def add(self, login: str, password: str, confirm: str,
            result: bool, error: str = "") -> None:
        """Добавить запись о регистрации."""
        self._conn.execute(
            "INSERT INTO registrations (login, password, confirm, result, error) "
            "VALUES (?, ?, ?, ?, ?)",
            (login, password, confirm, int(result), error),
        )
        self._conn.commit()

    def get(self, login: str, password: str, confirm: str) -> dict | None:
        """Получить запись по тройке (логин, пароль, подтверждение)."""
        row = self._conn.execute(
            "SELECT login, password, confirm, result, error "
            "FROM registrations WHERE login = ? AND password = ? AND confirm = ?",
            (login, password, confirm),
        ).fetchone()
        if row is None:
            return None
        record = dict(row)
        record["result"] = bool(record["result"])
        return record

    def delete(self, login: str, password: str, confirm: str) -> bool:
        """Удалить запись. Возвращает True, если строка была удалена."""
        cursor = self._conn.execute(
            "DELETE FROM registrations WHERE login = ? AND password = ? AND confirm = ?",
            (login, password, confirm),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self._conn.close()
