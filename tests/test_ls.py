"""Тесты для команды ls."""

import pytest
import os
from unittest.mock import Mock, patch, call
from pathlib import Path
from datetime import datetime
import stat as stat_module

from src.commands.filesystem import FileSystemCommands
from src.logger import ShellLogger


class TestLsCommand:
    """Тесты для команды ls."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.fs_commands = FileSystemCommands(self.logger)
        self.fs_commands.current_dir = "/test/dir"

    def test_ls_current_directory_simple(self):
        """Тест: ls без аргументов выводит содержимое текущей директории."""
        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.listdir', return_value=['file2.txt', 'file1.txt', 'folder1']), \
                patch('builtins.print') as mock_print:
            self.fs_commands.ls()

            # Проверяем что файлы выведены в отсортированном порядке
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert calls == ['file1.txt', 'file2.txt', 'folder1']
            self.logger.log_success.assert_called_once()

    def test_ls_with_path_argument(self):
        """Тест: ls с указанием пути."""
        target_path = "/test/dir/Documents"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.path.abspath') as mock_abspath, \
                patch('os.path.expanduser', return_value=target_path), \
                patch('os.listdir', return_value=['doc1.txt', 'doc2.pdf']), \
                patch('builtins.print') as mock_print:
            mock_abspath.return_value = target_path

            self.fs_commands.ls("Documents")

            # Проверяем что путь обработался правильно
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert calls == ['doc1.txt', 'doc2.pdf']

    def test_ls_long_format(self):
        """Тест: ls -l показывает детальную информацию."""
        mock_stat = Mock()
        mock_stat.st_size = 1024
        mock_stat.st_mtime = datetime(2023, 1, 15, 10, 30).timestamp()
        mock_stat.st_mode = 0o100644  # Обычный файл

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.listdir', return_value=['test.txt']), \
                patch('os.path.join', return_value='/test/dir/test.txt'), \
                patch('os.stat', return_value=mock_stat), \
                patch('stat.filemode', return_value='-rw-r--r--'), \
                patch('builtins.print') as mock_print:
            self.fs_commands.ls(detailed=True)

            # Проверяем что вывелась детальная информация
            assert mock_print.call_count >= 1
            # Проверяем что вывелась шапка таблицы
            first_call = mock_print.call_args_list[0][0][0]
            assert 'Name' in first_call and 'Size' in first_call

    def test_ls_nonexistent_path(self):
        """Тест: ls для несуществующего пути выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value='/nonexistent'), \
                patch('os.path.expanduser', return_value='/nonexistent'), \
                patch('builtins.print') as mock_print:
            self.fs_commands.ls("/nonexistent")

            # Проверяем что вывелось сообщение об ошибке
            error_call = mock_print.call_args_list[0][0][0]
            assert 'Error' in error_call
            self.logger.log_error.assert_called_once()

    def test_ls_not_a_directory(self):
        """Тест: ls для файла (не директории) выдаёт ошибку."""
        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=False), \
                patch('os.path.abspath', return_value='/test/file.txt'), \
                patch('os.path.expanduser', return_value='/test/file.txt'), \
                patch('builtins.print') as mock_print:
            self.fs_commands.ls("/test/file.txt")

            error_call = mock_print.call_args_list[0][0][0]
            assert 'Error' in error_call
            assert 'directory' in error_call.lower()

    def test_ls_empty_directory(self):
        """Тест: ls для пустой директории не выводит файлов."""
        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.listdir', return_value=[]), \
                patch('builtins.print') as mock_print:
            self.fs_commands.ls()

            # print не должен вызываться для пустой директории (кроме заголовка в -l режиме)
            assert mock_print.call_count == 0

    def test_ls_sorting_case_insensitive(self):
        """Тест: ls сортирует файлы без учёта регистра."""
        files = ['Zebra.txt', 'apple.txt', 'Banana.txt', 'cherry.txt']

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('os.listdir', return_value=files), \
                patch('builtins.print') as mock_print:
            self.fs_commands.ls()

            calls = [call[0][0] for call in mock_print.call_args_list]
            expected = ['apple.txt', 'Banana.txt', 'cherry.txt', 'Zebra.txt']
            assert calls == expected
