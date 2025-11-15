"""Тесты для команды cd."""

import pytest
import os
from unittest.mock import Mock, patch

from src.commands.filesystem import FileSystemCommands
from src.logger import ShellLogger


class TestCdCommand:
    """Тесты для команды cd."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.fs_commands = FileSystemCommands(self.logger)
        self.fs_commands.current_dir = "/home/user"

    def test_cd_to_subdirectory(self):
        """Тест: cd в подпапку."""
        target = "/home/user/Documents"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.path.abspath', return_value=target), \
                patch('os.path.join', return_value=target), \
                patch('os.chdir') as mock_chdir, \
                patch('builtins.print') as mock_print:
            self.fs_commands.cd("Documents")

            assert self.fs_commands.current_dir == target
            mock_chdir.assert_called_once_with(target)
            assert "Changed directory" in mock_print.call_args[0][0]

    def test_cd_to_parent_directory(self):
        """Тест: cd .. переходит в родительскую папку."""
        parent = "/home"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.path.dirname', return_value=parent), \
                patch('os.chdir') as mock_chdir, \
                patch('builtins.print'):
            self.fs_commands.cd("..")

            assert self.fs_commands.current_dir == parent
            mock_chdir.assert_called_once_with(parent)

    def test_cd_to_home_directory(self):
        """Тест: cd ~ переходит в домашнюю папку."""
        home = "/home/user"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.path.expanduser', return_value=home), \
                patch('os.chdir') as mock_chdir, \
                patch('builtins.print'):
            self.fs_commands.cd("~")

            mock_chdir.assert_called_once()

    def test_cd_absolute_path(self):
        """Тест: cd с абсолютным путём."""
        target = "/usr/local/bin"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.path.abspath', return_value=target), \
                patch('os.chdir') as mock_chdir, \
                patch('builtins.print'):
            self.fs_commands.cd(target)

            assert self.fs_commands.current_dir == target
            mock_chdir.assert_called_once_with(target)

    def test_cd_nonexistent_directory(self):
        """Тест: cd в несуществующую папку выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/nonexistent"), \
                patch('os.path.join', return_value="/nonexistent"), \
                patch('builtins.print') as mock_print:
            original_dir = self.fs_commands.current_dir
            self.fs_commands.cd("/nonexistent")

            # Директория не должна измениться
            assert self.fs_commands.current_dir == original_dir
            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            self.logger.log_error.assert_called_once()

    def test_cd_to_file_not_directory(self):
        """Тест: cd к файлу (не папке) выдаёт ошибку."""
        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=False), \
                patch('os.path.abspath', return_value="/home/user/file.txt"), \
                patch('os.path.join', return_value="/home/user/file.txt"), \
                patch('builtins.print') as mock_print:
            original_dir = self.fs_commands.current_dir
            self.fs_commands.cd("file.txt")

            assert self.fs_commands.current_dir == original_dir
            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            assert 'directory' in error_msg.lower()
