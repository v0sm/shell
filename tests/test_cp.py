"""Тесты для команды cp."""

import pytest
import os
import shutil
from unittest.mock import Mock, patch

from src.commands.filesystem import FileSystemCommands
from src.logger import ShellLogger


class TestCpCommand:
    """Тесты для команды cp."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.fs_commands = FileSystemCommands(self.logger)
        self.fs_commands.current_dir = "/test/dir"
        self.fs_commands.history = []

    def test_cp_file_to_file(self):
        """Тест: копирование файла в файл."""
        src = "/test/dir/source.txt"
        dst = "/test/dir/copy.txt"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst]), \
                patch('os.path.join', side_effect=[src, dst]), \
                patch('os.path.isdir', return_value=False), \
                patch('shutil.copy2') as mock_copy, \
                patch('builtins.print') as mock_print:
            self.fs_commands.cp("source.txt", "copy.txt")

            mock_copy.assert_called_once_with(src, dst)
            assert len(self.fs_commands.history) == 1
            assert self.fs_commands.history[0].startswith('cp|')
            assert 'SUCCESS' in mock_print.call_args[0][0] or 'Copied' in mock_print.call_args[0][0]

    def test_cp_file_to_directory(self):
        """Тест: копирование файла в директорию."""
        src = "/test/dir/file.txt"
        dst_dir = "/test/dir/backup"
        dst_file = "/test/dir/backup/file.txt"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst_dir]), \
                patch('os.path.join', side_effect=[src, dst_dir, dst_file]), \
                patch('os.path.isdir', side_effect=[False, True]), \
                patch('os.path.basename', return_value='file.txt'), \
                patch('shutil.copy2') as mock_copy, \
                patch('builtins.print'):
            self.fs_commands.cp("file.txt", "backup")

            # Файл должен скопироваться внутрь директории
            mock_copy.assert_called_once_with(src, dst_file)
            assert len(self.fs_commands.history) == 1

    def test_cp_directory_without_recursive(self):
        """Тест: копирование директории без -r выдаёт ошибку."""
        src = "/test/dir/folder"
        dst = "/test/dir/folder_copy"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst]), \
                patch('os.path.join', side_effect=[src, dst]), \
                patch('os.path.isdir', side_effect=[True]), \
                patch('builtins.print') as mock_print:
            self.fs_commands.cp("folder", "folder_copy", recursive=False)

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            assert 'recursive' in error_msg.lower() or '-r' in error_msg
            self.logger.log_error.assert_called_once()

    def test_cp_directory_with_recursive(self):
        """Тест: копирование директории с -r."""
        src = "/test/dir/folder"
        dst = "/test/dir/folder_copy"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst]), \
                patch('os.path.join', side_effect=[src, dst]), \
                patch('os.path.isdir', side_effect=[True]), \
                patch('shutil.copytree') as mock_copytree, \
                patch('builtins.print') as mock_print:
            self.fs_commands.cp("folder", "folder_copy", recursive=True)

            mock_copytree.assert_called_once_with(src, dst)
            assert len(self.fs_commands.history) == 1
            success_msg = mock_print.call_args[0][0]
            assert 'Copied' in success_msg or 'SUCCESS' in success_msg

    def test_cp_nonexistent_source(self):
        """Тест: копирование несуществующего файла выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent.txt"), \
                patch('os.path.join', return_value="/test/dir/nonexistent.txt"), \
                patch('builtins.print') as mock_print:
            self.fs_commands.cp("nonexistent.txt", "copy.txt")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            assert len(self.fs_commands.history) == 0  # Не должно сохраниться в истории
            self.logger.log_error.assert_called_once()

    def test_cp_creates_undo_entry(self):
        """Тест: cp создаёт запись для undo."""
        src = "/test/dir/original.txt"
        dst = "/test/dir/copy.txt"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[src, dst]), \
                patch('os.path.join', side_effect=[src, dst]), \
                patch('os.path.isdir', return_value=False), \
                patch('shutil.copy2'), \
                patch('builtins.print'):
            self.fs_commands.cp("original.txt", "copy.txt")

            # Проверяем формат записи для undo
            assert len(self.fs_commands.history) == 1
            undo_entry = self.fs_commands.history[0]
            assert undo_entry.startswith('cp|')
            assert src in undo_entry
            assert dst in undo_entry
