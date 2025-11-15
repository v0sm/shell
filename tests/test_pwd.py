"""Тесты для команды pwd."""

import pytest
from unittest.mock import Mock, patch

from src.commands.filesystem import FileSystemCommands
from src.logger import ShellLogger


class TestPwdCommand:
    """Тесты для команды pwd."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.fs_commands = FileSystemCommands(self.logger)

    def test_pwd_shows_current_directory(self):
        """Тест: pwd выводит текущую директорию."""
        self.fs_commands.current_dir = "/home/user/Documents"

        with patch('builtins.print') as mock_print:
            self.fs_commands.pwd()

            mock_print.assert_called_once_with("/home/user/Documents")
            self.logger.log_success.assert_called_once()

    def test_pwd_root_directory(self):
        """Тест: pwd для корневой директории."""
        self.fs_commands.current_dir = "/"

        with patch('builtins.print') as mock_print:
            self.fs_commands.pwd()

            mock_print.assert_called_once_with("/")

    def test_pwd_deep_nested_path(self):
        """Тест: pwd для глубоко вложенного пути."""
        deep_path = "/home/user/projects/python/shell/src/commands"
        self.fs_commands.current_dir = deep_path

        with patch('builtins.print') as mock_print:
            self.fs_commands.pwd()

            mock_print.assert_called_once_with(deep_path)

    def test_pwd_after_cd(self):
        """Тест: pwd после смены директории показывает новый путь."""
        self.fs_commands.current_dir = "/home/user"

        with patch('builtins.print') as mock_print:
            self.fs_commands.pwd()

            mock_print.assert_called_once_with("/home/user")

        self.fs_commands.current_dir = "/home/user/Documents"

        with patch('builtins.print') as mock_print:
            self.fs_commands.pwd()

            mock_print.assert_called_once_with("/home/user/Documents")
