"""Конфигурация pytest и общие фикстуры."""

import pytest
import os
import tempfile
import shutil

from src.logger import ShellLogger
from src.commands.filesystem import FileSystemCommands
from src.commands.archive import ArchiveCommands
from src.commands.advanced import AdvancedCommands


@pytest.fixture(scope='session')
def temp_dir():
    """Создаёт временную директорию для всей сессии тестов."""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def shell_logger(temp_dir):
    """Фикстура для инициализации ShellLogger."""
    log_file = os.path.join(temp_dir, 'test.log')
    return ShellLogger(log_file)


@pytest.fixture
def fs_commands(shell_logger, temp_dir):
    """Фикстура для FileSystemCommands с текущей директорией temp."""
    commands = FileSystemCommands(shell_logger)
    commands.current_dir = temp_dir
    os.chdir(temp_dir)
    return commands


@pytest.fixture
def archive_commands(shell_logger, temp_dir):
    """Фикстура для ArchiveCommands."""
    commands = ArchiveCommands(shell_logger)
    commands.current_dir = temp_dir
    os.chdir(temp_dir)
    return commands


@pytest.fixture
def advanced_commands(shell_logger, temp_dir):
    """Фикстура для AdvancedCommands."""
    commands = AdvancedCommands(shell_logger)
    commands.current_dir = temp_dir
    os.chdir(temp_dir)
    return commands
