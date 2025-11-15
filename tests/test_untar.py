"""Тесты для команды untar."""

import pytest
import os
import tarfile
from unittest.mock import Mock, patch, MagicMock

from src.commands.archive import ArchiveCommands
from src.logger import ShellLogger


class TestUntarCommand:
    """Тесты для команды untar."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.logger = Mock(spec=ShellLogger)
        self.archive_commands = ArchiveCommands(self.logger)
        self.archive_commands.current_dir = "/test/dir"

    def test_untar_archive(self):
        """Тест: распаковка tar.gz архива."""
        archive_path = "/test/dir/archive.tar.gz"

        mock_tar = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value=archive_path), \
                patch('os.path.join', return_value=archive_path), \
                patch('tarfile.open', return_value=mock_tar), \
                patch('builtins.print') as mock_print:
            mock_tar.__enter__ = Mock(return_value=mock_tar)
            mock_tar.__exit__ = Mock(return_value=False)

            self.archive_commands.untar_archive("archive.tar.gz")

            # extractall должен быть вызван с фильтром
            mock_tar.extractall.assert_called_once_with(
                self.archive_commands.current_dir,
                filter='data'
            )
            success_msg = mock_print.call_args[0][0]
            assert 'Extracted' in success_msg or 'SUCCESS' in success_msg

    def test_untar_nonexistent_archive(self):
        """Тест: распаковка несуществующего tar архива выдаёт ошибку."""
        with patch('os.path.exists', return_value=False), \
                patch('os.path.abspath', return_value="/test/dir/nonexistent.tar.gz"), \
                patch('os.path.join', return_value="/test/dir/nonexistent.tar.gz"), \
                patch('builtins.print') as mock_print:
            self.archive_commands.untar_archive("nonexistent.tar.gz")

            error_msg = mock_print.call_args[0][0]
            assert 'Error' in error_msg
            self.logger.log_error.assert_called_once()

    def test_untar_to_current_directory(self):
        """Тест: untar распаковывает в текущую директорию."""
        archive_path = "/test/dir/test.tar.gz"

        mock_tar = MagicMock()

        with patch('os.path.exists', return_value=True), \
                patch('os.path.abspath', return_value=archive_path), \
                patch('os.path.join', return_value=archive_path), \
                patch('tarfile.open', return_value=mock_tar), \
                patch('builtins.print'):
            mock_tar.__enter__ = Mock(return_value=mock_tar)
            mock_tar.__exit__ = Mock(return_value=False)

            self.archive_commands.untar_archive("test.tar.gz")

            # Проверяем что extractall вызван с правильной директорией
            call_args = mock_tar.extractall.call_args
            assert call_args[0][0] == "/test/dir"
            assert call_args[1]['filter'] == 'data'
