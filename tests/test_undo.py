"""Тесты для команды undo."""

import pytest
import os
import shutil
from unittest.mock import Mock, patch

from src.commands.advanced import AdvancedCommands
from src.logger import ShellLogger


class TestUndoCommand:
    """Тесты для команды undo."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.advanced_commands = AdvancedCommands(self.logger)
        self.advanced_commands.current_dir = "/test/dir"
        self.advanced_commands.history = []

    def test_undo_cp_removes_copy(self):
        """Тест: undo после cp удаляет скопированный файл."""
        src = "/test/dir/original.txt"
        dst = "/test/dir/copy.txt"
        self.advanced_commands.history = [f"cp|{src}|{dst}"]

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=False), \
                patch('os.remove') as mock_remove, \
                patch('builtins.print') as mock_print:
            self.advanced_commands.undo()

            # Скопированный файл должен быть удалён
            mock_remove.assert_called_once_with(dst)
            assert len(self.advanced_commands.history) == 0
            success_msg = str(mock_print.call_args_list)
            assert 'Undone' in success_msg or 'removed' in success_msg

    def test_undo_mv_moves_back(self):
        """Тест: undo после mv перемещает файл обратно."""
        src = "/test/dir/old.txt"
        dst = "/test/dir/new.txt"
        self.advanced_commands.history = [f"mv|{src}|{dst}"]

        with patch('os.path.exists', return_value=True), \
                patch('shutil.move') as mock_move, \
                patch('builtins.print') as mock_print:
            self.advanced_commands.undo()

            # Файл должен переместиться обратно
            mock_move.assert_called_once_with(dst, src)
            assert len(self.advanced_commands.history) == 0
            success_msg = str(mock_print.call_args_list)
            assert 'Undone' in success_msg or 'moved back' in success_msg

    def test_undo_rm_restores_from_trash(self):
        """Тест: undo после rm восстанавливает файл из корзины."""
        original = "/test/dir/deleted.txt"
        trash = "/test/dir/.trash/deleted.txt"
        self.advanced_commands.history = [f"rm|{original}|{trash}"]

        with patch('os.path.exists', return_value=True), \
                patch('shutil.move') as mock_move, \
                patch('builtins.print') as mock_print:
            self.advanced_commands.undo()

            # Файл должен переместиться из корзины обратно
            mock_move.assert_called_once_with(trash, original)
            assert len(self.advanced_commands.history) == 0
            success_msg = str(mock_print.call_args_list)
            assert 'Undone' in success_msg or 'restored' in success_msg

    def test_undo_empty_history(self):
        """Тест: undo без истории выводит сообщение."""
        self.advanced_commands.history = []

        with patch('builtins.print') as mock_print:
            self.advanced_commands.undo()

            # Должно вывестись "Nothing to undo"
            msg = mock_print.call_args[0][0]
            assert 'Nothing to undo' in msg

    def test_undo_skips_regular_commands(self):
        """Тест: undo пропускает обычные команды и находит последнюю отменяемую."""
        self.advanced_commands.history = [
            "cp|/test/file1|/test/copy1",
            "ls",
            "pwd",
            "cd Documents",
            "mv|/test/file2|/test/moved"
        ]

        with patch('os.path.exists', return_value=True), \
                patch('shutil.move'), \
                patch('builtins.print'):
            self.advanced_commands.undo()

            # Должна отменится последняя mv команда
            # В истории должно остаться 4 записи (mv удалена)
            assert len(self.advanced_commands.history) == 4
            assert "mv|" not in self.advanced_commands.history[-1]

    def test_undo_file_not_found(self):
        """Тест: undo когда файл уже не существует."""
        src = "/test/dir/original.txt"
        dst = "/test/dir/copy.txt"
        self.advanced_commands.history = [f"cp|{src}|{dst}"]

        with patch('os.path.exists', return_value=False), \
                patch('builtins.print') as mock_print:
            self.advanced_commands.undo()

            # Должно вывестись сообщение что файл не найден
            msg = str(mock_print.call_args_list)
            assert 'Cannot undo' in msg or 'not found' in msg

    def test_undo_cp_directory(self):
        """Тест: undo после cp -r удаляет скопированную директорию."""
        src = "/test/dir/original_folder"
        dst = "/test/dir/copy_folder"
        self.advanced_commands.history = [f"cp|{src}|{dst}"]

        with patch('os.path.exists', return_value=True), \
                patch('os.path.isdir', return_value=True), \
                patch('shutil.rmtree') as mock_rmtree, \
                patch('builtins.print'):
            self.advanced_commands.undo()

            # Скопированная папка должна быть удалена
            mock_rmtree.assert_called_once_with(dst)
            assert len(self.advanced_commands.history) == 0
