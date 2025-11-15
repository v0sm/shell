"""Конфигурация pytest и общие фикстуры для тестирования shell-эмулятора."""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Создаёт временную директорию для тестов.

    Фикстура автоматически создаёт временную папку перед тестом
    и удаляет её после завершения теста.

    Yields:
        Path: Путь к временной директории
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir: Path) -> dict[str, Path]:
    """
    Создаёт набор тестовых файлов и директорий.

    Полезно для интеграционных тестов, которым нужна реальная
    файловая структура.

    Args:
        temp_dir: Фикстура временной директории

    Returns:
        dict: Словарь с путями к созданным файлам и папкам
    """
    files = {}

    # Создаём тестовые файлы
    files['file1'] = temp_dir / 'file1.txt'
    files['file1'].write_text('Content of file 1', encoding='utf-8')

    files['file2'] = temp_dir / 'file2.txt'
    files['file2'].write_text('Content of file 2', encoding='utf-8')

    # Создаём тестовую директорию с файлами
    files['subdir'] = temp_dir / 'subdir'
    files['subdir'].mkdir()

    files['subfile'] = files['subdir'] / 'subfile.txt'
    files['subfile'].write_text('Content in subdirectory', encoding='utf-8')

    # Пустая директория
    files['empty_dir'] = temp_dir / 'empty_dir'
    files['empty_dir'].mkdir()

    return files


@pytest.fixture
def mock_logger():
    """
    Создаёт мок-объект логгера.

    Эта фикстура используется в большинстве unit-тестов для изоляции
    от реального логирования.

    Returns:
        Mock: Мок-объект ShellLogger
    """
    from unittest.mock import Mock
    from src.logger import ShellLogger

    logger = Mock(spec=ShellLogger)
    return logger


# Настройка pytest
def pytest_configure(config):
    """Конфигурация pytest перед запуском тестов."""
    # Добавляем маркеры для категоризации тестов
    config.addinivalue_line("markers", "unit: Unit tests with mocks")
    config.addinivalue_line("markers", "integration: Integration tests with real filesystem")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """
    Модифицирует собранные тесты перед выполнением.

    Автоматически помечает тесты с 'detailed' в имени как unit-тесты.
    """
    for item in items:
        # Автоматически помечаем детальные тесты как unit-тесты
        if "detailed" in item.nodeid:
            item.add_marker(pytest.mark.unit)
