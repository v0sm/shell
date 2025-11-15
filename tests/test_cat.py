"""Тесты для команды cat."""

import pytest
import os
from unittest.mock import Mock, patch, mock_open

from src.commands.filesystem import FileSystemCommands
from src.logger import ShellLogger


class TestCatCommand:
    """Тесты для команды cat."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.fs_commands = FileSystemCommands(self.logger)
        self.fs_commands.current_dir = "/test/dir"

    def test_cat_simple_file(self):
        """Тест: cat выводит содержимое файла."""
        file_content = "Hello, World!\nThis is a test file."

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/file.txt"), \
                patch('os.path.join', return_value="/test/dir/file.txt"), \
                patch('builtins.open', mock_open(read_data=file_content)), \
                patch('builtins.print') as mock_print:
            self.fs_commands.cat("file.txt")

            mock_print.assert_called_once_with(file_content)
            self.logger.log_success.assert_called_once()

    def test_cat_empty_file(self):
        """Тест: cat для пустого файла."""
        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/empty.txt"), \
                patch('os.path.join', return_value="/test/dir/empty.txt"), \
                patch('builtins.open', mock_open(read_data="")), \
                patch('builtins.print') as mock_print:
            self.fs_commands.cat("empty.txt")

            mock_print.assert_called_once_with("")

    def test_cat_multiline_file(self):
        """Тест: cat для многострочного файла."""
        content = "Line 1\nLine 2\nLine 3\nLine 4"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/multiline.txt"), \
                patch('os.path.join', return_value="/test/dir/multiline.txt"), \
                patch('builtins.open', mock_open(read_data=content)), \
                patch('builtins.print') as mock_print:
            self.fs_commands.cat("multiline.txt")

            # Весь файл должен вывестись целиком
            mock_print.assert_called_once_with(content)

    def test_cat_nonexistent_file(self):
        """Тест: cat для несуществующего файла выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent.txt"), \
                patch('os.path.join', return_value="/test/dir/nonexistent.txt"), \
                patch('builtins.print') as mock_print:
            self.fs_commands.cat("nonexistent.txt")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            self.logger.log_error.assert_called_once()

    def test_cat_directory(self):
        """Тест: cat для директории выдаёт ошибку."""
        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.path.abspath', return_value="/test/dir/folder"), \
                patch('os.path.join', return_value="/test/dir/folder"), \
                patch('builtins.print') as mock_print:
            self.fs_commands.cat("folder")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            assert 'directory' in error_msg.lower()

    def test_cat_utf8_file(self):
        """Тест: cat для файла с UTF-8 содержимым."""
        content = "Привет, мир! 你好世界! 🎉"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/utf8.txt"), \
                patch('os.path.join', return_value="/test/dir/utf8.txt"), \
                patch('builtins.open', mock_open(read_data=content)), \
                patch('builtins.print') as mock_print:
            self.fs_commands.cat("utf8.txt")

            mock_print.assert_called_once_with(content)
