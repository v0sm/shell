"""Модуль команд shell-эмулятора."""

from .filesystem import FileSystemCommands
from .archive import ArchiveCommands
from .advanced import AdvancedCommands
from ..logger import ShellLogger


class ShellCommands(FileSystemCommands, ArchiveCommands, AdvancedCommands):
    """
    Главный класс команд, объединяющий все модули.

    Использует множественное наследование для комбинирования
    команд из разных модулей.
    """

    def __init__(self, logger: ShellLogger) -> None:
        """
        Инициализация всех команд.

        Args:
            logger: Объект логгера
        """
        FileSystemCommands.__init__(self, logger)


__all__ = ['ShellCommands']
