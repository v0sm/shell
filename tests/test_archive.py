"""Тесты для команд работы с архивами."""

import pytest
import zipfile
import tarfile


@pytest.fixture
def temp_dir(tmp_path):
    """Создание временной директории для тестов."""
    return tmp_path

def test_zip_create_from_folder(archive_commands, temp_dir):
    """Тест создания ZIP архива из папки."""
    test_dir = temp_dir / 'testdir'
    test_dir.mkdir()
    (test_dir / 'file.txt').write_text('test content')

    archive_commands.zip_folder('testdir', 'archive.zip')

    archive_path = temp_dir / 'archive.zip'
    assert archive_path.exists()

    with zipfile.ZipFile(archive_path, 'r') as zf:
        assert 'testdir/file.txt' in zf.namelist()


def test_zip_create_from_file(archive_commands, temp_dir):
    """Тест создания ZIP архива из одного файла."""
    test_file = temp_dir / 'test.txt'
    test_file.write_text('test content')

    archive_commands.zip_folder('test.txt', 'archive.zip')

    archive_path = temp_dir / 'archive.zip'
    assert archive_path.exists()


def test_zip_nonexistent_folder(archive_commands, capsys):
    """Тест создания архива из несуществующей папки."""
    archive_commands.zip_folder('nonexistent', 'archive.zip')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_unzip_archive(archive_commands, temp_dir):
    """Тест распаковки ZIP архива."""
    archive_path = temp_dir / 'archive.zip'
    with zipfile.ZipFile(archive_path, 'w') as zf:
        zf.writestr('extracted_file.txt', 'test content')

    archive_commands.unzip_archive('archive.zip')

    assert (temp_dir / 'extracted_file.txt').exists()


def test_unzip_nonexistent_archive(archive_commands, capsys):
    """Тест распаковки несуществующего архива."""
    archive_commands.unzip_archive('nonexistent.zip')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_tar_create_from_folder(archive_commands, temp_dir):
    """Тест создания TAR.GZ архива из папки."""
    test_dir = temp_dir / 'testdir'
    test_dir.mkdir()
    (test_dir / 'file.txt').write_text('test content')

    archive_commands.tar_folder('testdir', 'archive.tar.gz')

    archive_path = temp_dir / 'archive.tar.gz'
    assert archive_path.exists()

    with tarfile.open(archive_path, 'r:gz') as tf:
        names = tf.getnames()
        assert any('testdir' in name for name in names)


def test_untar_archive(archive_commands, temp_dir):
    """Тест распаковки TAR.GZ архива."""
    archive_path = temp_dir / 'archive.tar.gz'
    with tarfile.open(archive_path, 'w:gz') as tf:
        test_file = temp_dir / 'temp_file.txt'
        test_file.write_text('test content')
        tf.add(test_file, arcname='extracted_file.txt')
        test_file.unlink()

    archive_commands.untar_archive('archive.tar.gz')

    assert (temp_dir / 'extracted_file.txt').exists()


def test_untar_nonexistent_archive(archive_commands, capsys):
    """Тест распаковки несуществующего TAR архива."""
    archive_commands.untar_archive('nonexistent.tar.gz')
    captured = capsys.readouterr()
    assert 'Error' in captured.out
