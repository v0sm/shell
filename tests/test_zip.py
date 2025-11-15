"""Тесты для команды zip."""

import pytest
import os
import zipfile
from unittest.mock import Mock, patch, MagicMock

from src.commands.archive import ArchiveCommands
from src.logger import ShellLogger


class TestZipCommand:
    """Тесты для команды zip."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.archive_commands = ArchiveCommands(self.logger)
        self.archive_commands.current_dir = "/test/dir"

    def test_zip_single_file(self):
        """Тест: создание zip архива из одного файла."""
        folder_path = "/test/dir/file.txt"
        archive_path = "/test/dir/archive.zip"

        mock_zipf = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[folder_path, archive_path]), \
                patch('os.path.join', side_effect=[folder_path, archive_path]), \
                patch('os.path.isfile', return_value=True), \
                patch('os.path.basename', return_value='file.txt'), \
                patch('zipfile.ZipFile', return_value=mock_zipf) as mock_zip_class, \
                patch('builtins.print') as mock_print:
            mock_zipf.__enter__ = Mock(return_value=mock_zipf)
            mock_zipf.__exit__ = Mock(return_value=False)

            self.archive_commands.zip_folder("file.txt", "archive.zip")

            # Проверяем что ZipFile был создан
            mock_zip_class.assert_called_once_with(archive_path, 'w', zipfile.ZIP_DEFLATED)
            # Файл должен быть добавлен в архив
            mock_zipf.write.assert_called_once()
            success_msg = mock_print.call_args[0][0]
            assert 'Created' in success_msg or 'SUCCESS' in success_msg

    def test_zip_folder(self):
        """Тест: создание zip архива из папки."""
        folder_path = "/test/dir/myfolder"
        archive_path = "/test/dir/archive.zip"

        mock_zipf = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[folder_path, archive_path]), \
                patch('os.path.join', side_effect=[folder_path, archive_path, "/test/dir/myfolder/file1.txt"]), \
                patch('os.path.isfile', return_value=False), \
                patch('os.walk', return_value=[
                    ("/test/dir/myfolder", [], ["file1.txt", "file2.txt"])
                ]), \
                patch('os.path.relpath', side_effect=lambda path, start: "myfolder/file1.txt"), \
                patch('os.path.dirname', return_value="/test/dir"), \
                patch('zipfile.ZipFile', return_value=mock_zipf), \
                patch('builtins.print'):
            mock_zipf.__enter__ = Mock(return_value=mock_zipf)
            mock_zipf.__exit__ = Mock(return_value=False)

            self.archive_commands.zip_folder("myfolder", "archive.zip")

            # Файлы из папки должны быть добавлены
            assert mock_zipf.write.call_count >= 1

    def test_zip_nonexistent_folder(self):
        """Тест: создание архива из несуществующей папки выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent"), \
                patch('os.path.join', return_value="/test/dir/nonexistent"), \
                patch('builtins.print') as mock_print:
            self.archive_commands.zip_folder("nonexistent", "archive.zip")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            self.logger.log_error.assert_called_once()

    def test_zip_empty_folder(self):
        """Тест: создание архива из пустой папки."""
        folder_path = "/test/dir/empty_folder"
        archive_path = "/test/dir/empty.zip"

        mock_zipf = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', side_effect=[folder_path, archive_path]), \
                patch('os.path.join', side_effect=[folder_path, archive_path]), \
                patch('os.path.isfile', return_value=False), \
                patch('os.walk', return_value=[
                    ("/test/dir/empty_folder", [], [])  # Пустая папка
                ]), \
                patch('zipfile.ZipFile', return_value=mock_zipf), \
                patch('builtins.print') as mock_print:
            mock_zipf.__enter__ = Mock(return_value=mock_zipf)
            mock_zipf.__exit__ = Mock(return_value=False)

            self.archive_commands.zip_folder("empty_folder", "empty.zip")

            # Архив должен создаться, даже если папка пустая
            success_msg = mock_print.call_args[0][0]
            assert 'Created' in success_msg or 'SUCCESS' in success_msg
