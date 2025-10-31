"""Базовый класс для команд shell-эмулятора."""

import os
from typing import List

from ..logger import ShellLogger
from ..constants import HISTORY_FILE, TRASH_DIR, MAX_HISTORY_SIZE


class BaseCommands:
    """Базовый класс с общими методами для всех команд."""

    def __init__(self, logger: ShellLogger) -> None:
        """
        Инициализация базового класса команд.

        Args:
            logger: Объект логгера для записи операций
        """
        self.logger = logger
        self.current_dir: str = os.getcwd()
        self.history: List[str] = []
        self.history_file: str = HISTORY_FILE
        self.trash_dir: str = TRASH_DIR
        self._initialize_dirs()
        self.load_history()

    def _initialize_dirs(self) -> None:
        """Создание необходимых директорий."""
        if not os.path.exists(self.trash_dir):
            os.makedirs(self.trash_dir)

    def load_history(self) -> None:
        """Загрузка истории команд из файла."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = [line.strip() for line in f.readlines()]
            except Exception as e:
                self.logger.log_error(f"Failed to load history: {e}")

    def save_history(self) -> None:
        """Сохранение истории команд в файл."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                for cmd in self.history[-MAX_HISTORY_SIZE:]:
                    f.write(cmd + '\n')
        except Exception as e:
            self.logger.log_error(f"Failed to save history: {e}")

    def add_to_history(self, command: str) -> None:
        """
        Добавление команды в историю.

        Args:
            command: Команда для добавления
        """
        self.history.append(command)
        if len(self.history) > MAX_HISTORY_SIZE:
            self.history = self.history[-MAX_HISTORY_SIZE:]
        self.save_history()

    def resolve_path(self, path: str) -> str:
        """
        Разрешение относительного или абсолютного пути.

        Args:
            path: Исходный путь

        Returns:
            Абсолютный путь
        """
        if path == '~':
            return os.path.expanduser('~')
        elif path == '..':
            return os.path.dirname(self.current_dir)
        else:
            return os.path.abspath(os.path.join(self.current_dir, path))
