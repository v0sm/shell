"""Тесты для команды mv."""

import pytest
import os
import shutil
from unittest.mock import Mock, patch

from src.commands.filesystem import FileSystemCommands
from src.logger import ShellLogger


class TestMvCommand:
    """Тесты для команды mv."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.fs_commands = FileSystemCommands(self.logger)
        self.fs_commands.current_dir = "/test/dir"
        self.fs_commands.history = []

    def test_mv_file_rename(self):
        """Тест: переименование файла (mv в той же директории)."""
        src = "/test/dir/old.txt"
        dst = "/test/dir/new.txt"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst]), \
                patch('os.path.join', side_effect=[src, dst]), \
                patch('shutil.move') as mock_move, \
                patch('builtins.print') as mock_print:
            self.fs_commands.mv("old.txt", "new.txt")

            mock_move.assert_called_once_with(src, dst)
            assert len(self.fs_commands.history) == 1
            assert self.fs_commands.history[0].startswith('mv|')
            success_msg = mock_print.call_args[0][0]
            assert 'Moved' in success_msg or 'SUCCESS' in success_msg

    def test_mv_file_to_directory(self):
        """Тест: перемещение файла в другую директорию."""
        src = "/test/dir/file.txt"
        dst = "/test/dir/Documents"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst]), \
                patch('os.path.join', side_effect=[src, dst]), \
                patch('shutil.move') as mock_move, \
                patch('builtins.print'):
            self.fs_commands.mv("file.txt", "Documents")

            mock_move.assert_called_once_with(src, dst)
            assert len(self.fs_commands.history) == 1

    def test_mv_directory(self):
        """Тест: перемещение директории."""
        src = "/test/dir/old_folder"
        dst = "/test/dir/new_folder"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst]), \
                patch('os.path.join', side_effect=[src, dst]), \
                patch('shutil.move') as mock_move, \
                patch('builtins.print'):
            self.fs_commands.mv("old_folder", "new_folder")

            mock_move.assert_called_once_with(src, dst)
            assert len(self.fs_commands.history) == 1

    def test_mv_nonexistent_source(self):
        """Тест: перемещение несуществующего файла выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent.txt"), \
                patch('os.path.join', return_value="/test/dir/nonexistent.txt"), \
                patch('builtins.print') as mock_print:
            self.fs_commands.mv("nonexistent.txt", "target.txt")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            assert len(self.fs_commands.history) == 0
            self.logger.log_error.assert_called_once()

    def test_mv_creates_undo_entry(self):
        """Тест: mv создаёт запись для undo с правильным форматом."""
        src = "/test/dir/source.txt"
        dst = "/test/dir/destination.txt"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst]), \
                patch('os.path.join', side_effect=[src, dst]), \
                patch('shutil.move'), \
                patch('builtins.print'):
            self.fs_commands.mv("source.txt", "destination.txt")

            assert len(self.fs_commands.history) == 1
            undo_entry = self.fs_commands.history[0]
            assert undo_entry.startswith('mv|')
            parts = undo_entry.split('|')
            assert len(parts) == 3
            assert parts[1] == src
            assert parts[2] == dst
