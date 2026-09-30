import logging
import sys
from pathlib import Path

# Папка для логов создаётся в директории с конфигом
LOG_DIR = Path(__file__).resolve().parent / "Logs"
LOG_FILE = LOG_DIR / "file_txt.log"

# Шаблон строки лога: время | уровень (выравнивание до 7 символов) | сообщение
log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"


def setup_logger() -> None:
    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,  # минимальный порог важности
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # вывод в консоль
            logging.FileHandler(LOG_FILE, encoding="utf-8"),  # вывод в файл
        ],
        force=True,  # переопределяем возможную предыдущую конфигурацию
    )

    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")