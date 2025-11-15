"""Тесты для команды grep."""

import pytest
import os
import re
from unittest.mock import Mock, patch, mock_open

from src.commands.advanced import AdvancedCommands
from src.logger import ShellLogger


class TestGrepCommand:
    """Тесты для команды grep."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.advanced_commands = AdvancedCommands(self.logger)
        self.advanced_commands.current_dir = "/test/dir"

    def test_grep_find_pattern_in_file(self):
        """Тест: grep находит паттерн в файле."""
        file_content = "Line 1: Hello\nLine 2: World\nLine 3: Hello again"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value="/test/dir/test.txt"), \
                patch('os.path.join', return_value="/test/dir/test.txt"), \
                patch('os.path.isfile', return_value=True), \
                patch('builtins.open', mock_open(read_data=file_content)), \
                patch('builtins.print') as mock_print:
            self.advanced_commands.grep("Hello", "test.txt")

            # Должны вывестись строки с "Hello"
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('Hello' in call for call in calls)
            # Должны быть номера строк
            assert any(':1:' in call or 'Line 1' in call for call in calls)

    def test_grep_case_insensitive(self):
        """Тест: grep с опцией -i игнорирует регистр."""
        file_content = "hello world\nHELLO WORLD\nHeLLo WoRLd"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value="/test/dir/test.txt"), \
                patch('os.path.join', return_value="/test/dir/test.txt"), \
                patch('os.path.isfile', return_value=True), \
                patch('builtins.open', mock_open(read_data=file_content)), \
                patch('builtins.print') as mock_print:
            self.advanced_commands.grep("HELLO", "test.txt", ignore_case=True)

            # Все три строки должны совпасть
            assert mock_print.call_count >= 3

    def test_grep_no_matches(self):
        """Тест: grep не находит совпадений."""
        file_content = "Line 1\nLine 2\nLine 3"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value="/test/dir/test.txt"), \
                patch('os.path.join', return_value="/test/dir/test.txt"), \
                patch('os.path.isfile', return_value=True), \
                patch('builtins.open', mock_open(read_data=file_content)), \
                patch('builtins.print') as mock_print:
            self.advanced_commands.grep("NotFound", "test.txt")

            # Должно вывестись сообщение "No matches found"
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('No matches' in call for call in calls)

    def test_grep_recursive_in_directory(self):
        """Тест: grep -r ищет рекурсивно в директории."""
        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value="/test/dir/folder"), \
                patch('os.path.join', side_effect=lambda *args: '/'.join(args)), \
                patch('os.path.isfile', return_value=False), \
                patch('os.path.isdir', return_value=True), \
                patch('os.walk', return_value=[
                    ("/test/dir/folder", [], ["file1.txt", "file2.txt"])
                ]), \
                patch('builtins.open', mock_open(read_data="test pattern")), \
                patch('builtins.print') as mock_print:
            self.advanced_commands.grep("pattern", "folder", recursive=True)

            # Должны проверяться файлы рекурсивно
            assert mock_print.call_count >= 1

    def test_grep_nonexistent_path(self):
        """Тест: grep для несуществующего пути выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent"), \
                patch('os.path.join', return_value="/test/dir/nonexistent"), \
                patch('builtins.print') as mock_print:
            self.advanced_commands.grep("pattern", "nonexistent")

            error_call = mock_print.call_args_list[0][0][0]
            assert 'Error' in error_call
            self.logger.log_error.assert_called_once()

    def test_grep_regex_pattern(self):
        """Тест: grep поддерживает регулярные выражения."""
        file_content = "test123\ntest456\nabc789"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value="/test/dir/test.txt"), \
                patch('os.path.join', return_value="/test/dir/test.txt"), \
                patch('os.path.isfile', return_value=True), \
                patch('builtins.open', mock_open(read_data=file_content)), \
                patch('builtins.print') as mock_print:
            self.advanced_commands.grep(r"test\d+", "test.txt")

            # Должны найтись test123 и test456, но не abc789
            calls = [str(call) for call in mock_print.call_args_list]
            matching_calls = [c for c in calls if 'test' in c]
            assert len(matching_calls) >= 2
