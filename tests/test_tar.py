"""Тесты для команды tar."""

import pytest
import os
import tarfile
from unittest.mock import Mock, patch, MagicMock

from src.commands.archive import ArchiveCommands
from src.logger import ShellLogger


class TestTarCommand:
    """Тесты для команды tar."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.archive_commands = ArchiveCommands(self.logger)
        self.archive_commands.current_dir = "/test/dir"

    def test_tar_folder(self):
        """Тест: создание tar.gz архива из папки."""
        folder_path = "/test/dir/myfolder"
        archive_path = "/test/dir/archive.tar.gz"

        mock_tar = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[folder_path, archive_path]), \
                patch('os.path.join', side_effect=[folder_path, archive_path]), \
                patch('os.path.basename', return_value='myfolder'), \
                patch('tarfile.open', return_value=mock_tar), \
                patch('builtins.print') as mock_print:
            mock_tar.__enter__ = Mock(return_value=mock_tar)
            mock_tar.__exit__ = Mock(return_value=False)

            self.archive_commands.tar_folder("myfolder", "archive.tar.gz")

            # Проверяем что tarfile.open вызван с правильными параметрами
            tarfile.open.assert_called_once_with(archive_path, 'w:gz')
            # Папка должна быть добавлена в архив
            mock_tar.add.assert_called_once_with(folder_path, arcname='myfolder')
            success_msg = mock_print.call_args[0][0]
            assert 'Created' in success_msg or 'SUCCESS' in success_msg

    def test_tar_single_file(self):
        """Тест: создание tar.gz архива из файла."""
        file_path = "/test/dir/file.txt"
        archive_path = "/test/dir/file.tar.gz"

        mock_tar = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[file_path, archive_path]), \
                patch('os.path.join', side_effect=[file_path, archive_path]), \
                patch('os.path.basename', return_value='file.txt'), \
                patch('tarfile.open', return_value=mock_tar), \
                patch('builtins.print'):
            mock_tar.__enter__ = Mock(return_value=mock_tar)
            mock_tar.__exit__ = Mock(return_value=False)

            self.archive_commands.tar_folder("file.txt", "file.tar.gz")

            # Файл должен быть добавлен
            mock_tar.add.assert_called_once()

    def test_tar_nonexistent_folder(self):
        """Тест: создание tar архива из несуществующей папки выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent"), \
                patch('os.path.join', return_value="/test/dir/nonexistent"), \
                patch('builtins.print') as mock_print:
            self.archive_commands.tar_folder("nonexistent", "archive.tar.gz")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            self.logger.log_error.assert_called_once()
