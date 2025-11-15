"""Тесты для команды rm."""

import pytest
import os
import shutil
from unittest.mock import Mock, patch, call

from src.commands.filesystem import FileSystemCommands
from src.logger import ShellLogger


class TestRmCommand:
    """Тесты для команды rm."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.fs_commands = FileSystemCommands(self.logger)
        self.fs_commands.current_dir = "/test/dir"
        self.fs_commands.trash_dir = ".trash"
        self.fs_commands.history = []

    def test_rm_file_moves_to_trash(self):
        """Тест: удаление файла перемещает его в корзину."""
        target = "/test/dir/file.txt"
        trash_dir = "/test/dir/.trash"
        trash_file = "/test/dir/.trash/file.txt"

        with patch('os.path.exists') as mock_exists, \
                patch('os.path.abspath', return_value=target), \
                patch('os.path.join') as mock_join, \
                patch('os.path.dirname', return_value="/test"), \
                patch('os.path.isdir', return_value=False), \
                patch('os.path.basename', return_value='file.txt'), \
                patch('os.makedirs'), \
                patch('shutil.move') as mock_move, \
                patch('builtins.print') as mock_print:

            # Первый вызов - проверка файла, второй - проверка корзины, третий - проверка trash_file
            mock_exists.side_effect = [True, True, False]

            def join_side_effect(*args):
                if len(args) == 2:
                    if args[1] == 'file.txt':
                        return target
                    elif args[1] == '.trash':
                        return trash_dir
                    elif 'file.txt' in str(args):
                        return trash_file
                return '/'.join(args)

            mock_join.side_effect = join_side_effect

            self.fs_commands.rm("file.txt")

            # Файл должен переместиться в корзину
            mock_move.assert_called_once()
            assert len(self.fs_commands.history) == 1
            assert self.fs_commands.history[0].startswith('rm|')

    def test_rm_directory_without_recursive(self):
        """Тест: удаление директории без -r выдаёт ошибку."""
        target = "/test/dir/folder"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value=target), \
                patch('os.path.join', return_value=target), \
                patch('os.path.dirname', return_value="/test"), \
                patch('os.path.isdir', return_value=True), \
                patch('builtins.print') as mock_print:
            self.fs_commands.rm("folder", recursive=False)

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            assert 'recursive' in error_msg.lower() or '-r' in error_msg
            assert len(self.fs_commands.history) == 0

    def test_rm_directory_with_recursive_and_confirmation(self):
        """Тест: удаление директории с -r требует подтверждения."""
        target = "/test/dir/folder"
        trash_dir = "/test/dir/.trash"
        trash_folder = "/test/dir/.trash/folder"

        with patch('os.path.exists') as mock_exists, \
                patch('os.path.abspath', return_value=target), \
                patch('os.path.join') as mock_join, \
                patch('os.path.dirname', return_value="/test"), \
                patch('os.path.isdir', return_value=True), \
                patch('os.path.basename', return_value='folder'), \
                patch('os.makedirs'), \
                patch('builtins.input', return_value='y'), \
                patch('shutil.move') as mock_move, \
                patch('builtins.print'):

            mock_exists.side_effect = [True, True, False]

            def join_side_effect(*args):
                if len(args) == 2:
                    if args[1] == 'folder':
                        return target
                    elif args[1] == '.trash':
                        return trash_dir
                    elif 'folder' in str(args):
                        return trash_folder
                return '/'.join(args)

            mock_join.side_effect = join_side_effect

            self.fs_commands.rm("folder", recursive=True)

            mock_move.assert_called_once()
            assert len(self.fs_commands.history) == 1

    def test_rm_directory_cancelled(self):
        """Тест: отмена удаления директории при вводе 'n'."""
        target = "/test/dir/important_folder"

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value=target), \
                patch('os.path.join', return_value=target), \
                patch('os.path.dirname', return_value="/test"), \
                patch('os.path.isdir', return_value=True), \
                patch('builtins.input', return_value='n'), \
                patch('builtins.print') as mock_print:
            self.fs_commands.rm("important_folder", recursive=True)

            assert any('Cancelled' in str(call) for call in mock_print.call_args_list)
            assert len(self.fs_commands.history) == 0

    def test_rm_nonexistent_file(self):
        """Тест: удаление несуществующего файла выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent.txt"), \
                patch('os.path.join', return_value="/test/dir/nonexistent.txt"), \
                patch('os.path.dirname', return_value="/test"), \
                patch('builtins.print') as mock_print:
            self.fs_commands.rm("nonexistent.txt")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            assert len(self.fs_commands.history) == 0
            self.logger.log_error.assert_called_once()

    def test_rm_root_directory_protection(self):
        """Тест: защита от удаления корневых директорий."""
        with patch('os.path.abspath', return_value="/"), \
                patch('os.path.join', return_value="/"), \
                patch('builtins.print') as mock_print:
            self.fs_commands.rm("/")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            assert 'root' in error_msg.lower() or 'cannot remove' in error_msg.lower()

    def test_rm_creates_undo_entry(self):
        """Тест: rm создаёт правильную запись для undo."""
        target = "/test/dir/deleteme.txt"
        trash_dir = "/test/dir/.trash"
        trash_file = "/test/dir/.trash/deleteme.txt"

        with patch('os.path.exists') as mock_exists, \
                patch('os.path.abspath', return_value=target), \
                patch('os.path.join') as mock_join, \
                patch('os.path.dirname', return_value="/test"), \
                patch('os.path.isdir', return_value=False), \
                patch('os.path.basename', return_value='deleteme.txt'), \
                patch('os.makedirs'), \
                patch('shutil.move'), \
                patch('builtins.print'):

            mock_exists.side_effect = [True, True, False]

            def join_side_effect(*args):
                if len(args) == 2:
                    if args[1] == 'deleteme.txt':
                        return target
                    elif args[1] == '.trash':
                        return trash_dir
                    elif 'deleteme.txt' in str(args):
                        return trash_file
                return '/'.join(args)

            mock_join.side_effect = join_side_effect

            self.fs_commands.rm("deleteme.txt")

            assert len(self.fs_commands.history) == 1
            undo_entry = self.fs_commands.history[0]
            assert undo_entry.startswith('rm|')
            parts = undo_entry.split('|')
            assert len(parts) == 3
            assert parts[1] == target

