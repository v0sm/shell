"""Модуль для логирования команд shell-эмулятора."""

import logging

from .constants import LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT


class ShellLogger:
    """Класс для логирования команд и ошибок shell-эмулятора."""

    def __init__(self, log_file: str = LOG_FILE) -> None:
        """
        Инициализация логгера.

        Args:
            log_file: Путь к файлу логов
        """
        self.log_file = log_file
        self.logger = logging.getLogger('ShellLogger')
        self.logger.setLevel(logging.INFO)

        self.logger.handlers.clear()

        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_command(self, command: str) -> None:
        """
        Логирование выполненной команды.

        Args:
            command: Строка с командой
        """
        self.logger.info(command)

    def log_error(self, error_message: str) -> None:
        """
        Логирование ошибки.

        Args:
            error_message: Текст ошибки
        """
        self.logger.error(f"ERROR: {error_message}")

    def log_success(self, message: str) -> None:
        """
        Логирование успешной операции.

        Args:
            message: Сообщение об успехе
        """
        self.logger.info(f"SUCCESS: {message}")
