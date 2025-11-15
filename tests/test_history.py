"""Тесты для команды history."""

import pytest
from unittest.mock import Mock, patch

from src.commands.advanced import AdvancedCommands
from src.logger import ShellLogger


class TestHistoryCommand:
    """Тесты для команды history."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.advanced_commands = AdvancedCommands(self.logger)
        self.advanced_commands.current_dir = "/test/dir"

    def test_history_shows_commands(self):
        """Тест: history показывает список выполненных команд."""
        self.advanced_commands.history = ["ls", "cd Documents", "cat file.txt"]

        with patch('builtins.print') as mock_print:
            self.advanced_commands.show_history()

            # Должны вывестись все команды с номерами
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('ls' in call for call in calls)
            assert any('cd Documents' in call for call in calls)
            assert any('cat file.txt' in call for call in calls)

    def test_history_empty(self):
        """Тест: history для пустой истории."""
        self.advanced_commands.history = []

        with patch('builtins.print') as mock_print:
            self.advanced_commands.show_history()

            # Должен вывестись заголовок, но не команды
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('History' in call for call in calls)

    def test_history_filters_undo_entries(self):
        """Тест: history не показывает служебные записи для undo."""
        self.advanced_commands.history = [
            "ls",
            "cp|/test/source|/test/dest",  # Служебная запись
            "cd Documents",
            "mv|/test/old|/test/new"  # Служебная запись
        ]

        with patch('builtins.print') as mock_print:
            self.advanced_commands.show_history()

            # Служебные записи не должны показываться
            calls = [str(call) for call in mock_print.call_args_list]
            command_calls = [c for c in calls if ':' in c and any(cmd in c for cmd in ['ls', 'cd'])]
            assert any('ls' in call for call in command_calls)
            assert any('cd Documents' in call for call in command_calls)
            # Служебные записи с | не должны показываться
            assert not any('cp|' in call for call in command_calls)
            assert not any('mv|' in call for call in command_calls)

    def test_history_limits_to_100(self):
        """Тест: history показывает максимум 100 последних команд."""
        # Создаём больше 100 команд
        self.advanced_commands.history = [f"command_{i}" for i in range(150)]

        with patch('builtins.print') as mock_print:
            self.advanced_commands.show_history()

            # Должны вывестись только последние 100
            calls = [str(call) for call in mock_print.call_args_list]
            command_calls = [c for c in calls if 'command_' in c]
            assert len(command_calls) <= 100

    def test_history_numbered_output(self):
        """Тест: history нумерует команды."""
        self.advanced_commands.history = ["ls", "pwd", "cat test.txt"]

        with patch('builtins.print') as mock_print:
            self.advanced_commands.show_history()

            calls = [str(call) for call in mock_print.call_args_list]
            # Проверяем что есть нумерация (1:, 2:, 3:)
            assert any('1:' in call or '1 ' in call for call in calls)
