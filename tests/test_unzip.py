"""Тесты для команды unzip."""

import pytest
import os
import zipfile
from unittest.mock import Mock, patch, MagicMock

from src.commands.archive import ArchiveCommands
from src.logger import ShellLogger


class TestUnzipCommand:
    """Тесты для команды unzip."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.archive_commands = ArchiveCommands(self.logger)
        self.archive_commands.current_dir = "/test/dir"

    def test_unzip_archive(self):
        """Тест: распаковка zip архива."""
        archive_path = "/test/dir/archive.zip"

        mock_zipf = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value=archive_path), \
                patch('os.path.join', return_value=archive_path), \
                patch('zipfile.ZipFile', return_value=mock_zipf), \
                patch('builtins.print') as mock_print:
            mock_zipf.__enter__ = Mock(return_value=mock_zipf)
            mock_zipf.__exit__ = Mock(return_value=False)

            self.archive_commands.unzip_archive("archive.zip")

            # extractall должен быть вызван
            mock_zipf.extractall.assert_called_once_with(self.archive_commands.current_dir)
            success_msg = mock_print.call_args[0][0]
            assert 'Extracted' in success_msg or 'SUCCESS' in success_msg

    def test_unzip_nonexistent_archive(self):
        """Тест: распаковка несуществующего архива выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent.zip"), \
                patch('os.path.join', return_value="/test/dir/nonexistent.zip"), \
                patch('builtins.print') as mock_print:
            self.archive_commands.unzip_archive("nonexistent.zip")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            self.logger.log_error.assert_called_once()

    def test_unzip_to_current_directory(self):
        """Тест: unzip распаковывает в текущую директорию."""
        archive_path = "/test/dir/test.zip"

        mock_zipf = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value=archive_path), \
                patch('os.path.join', return_value=archive_path), \
                patch('zipfile.ZipFile', return_value=mock_zipf), \
                patch('builtins.print'):
            mock_zipf.__enter__ = Mock(return_value=mock_zipf)
            mock_zipf.__exit__ = Mock(return_value=False)

            self.archive_commands.unzip_archive("test.zip")

            # Проверяем что extractall вызван с правильной директорией
            mock_zipf.extractall.assert_called_once()
            call_args = mock_zipf.extractall.call_args[0]
            assert call_args[0] == "/test/dir"
