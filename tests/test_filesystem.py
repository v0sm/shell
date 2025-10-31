"""Тесты для команд файловой системы."""

import pytest


@pytest.fixture
def temp_dir(tmp_path):
    """Создание временной директории для тестов."""
    return tmp_path

def test_ls_existing_directory(fs_commands, temp_dir):
    """Тест команды ls для существующей директории."""
    test_file = temp_dir / 'test.txt'
    test_file.touch()

    fs_commands.ls(str(temp_dir))
    assert test_file.exists()


def test_ls_nonexistent_directory(fs_commands, capsys):
    """Тест команды ls для несуществующей директории."""
    fs_commands.ls('/nonexistent/path/that/does/not/exist')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_ls_detailed_output(fs_commands, temp_dir):
    """Тест команды ls с опцией -l."""
    test_file = temp_dir / 'test.txt'
    test_file.touch()

    fs_commands.ls(str(temp_dir), detailed=True)
    assert test_file.exists()


def test_cd_to_existing_directory(fs_commands, temp_dir):
    """Тест команды cd для существующей директории."""
    subdir = temp_dir / 'subdir'
    subdir.mkdir()

    fs_commands.cd('subdir')
    assert fs_commands.current_dir == str(subdir)


def test_cd_to_nonexistent_directory(fs_commands, capsys):
    """Тест команды cd для несуществующей директории."""
    fs_commands.cd('/nonexistent/directory')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_cd_to_parent_directory(fs_commands, temp_dir):
    """Тест команды cd для перехода на уровень выше."""
    subdir = temp_dir / 'subdir'
    subdir.mkdir()
    fs_commands.cd('subdir')

    fs_commands.cd('..')
    assert fs_commands.current_dir == str(temp_dir)


def test_cat_existing_file(fs_commands, temp_dir, capsys):
    """Тест команды cat для существующего файла."""
    test_file = temp_dir / 'test.txt'
    test_content = 'Hello, World!'

    with open(test_file, 'w') as f:
        f.write(test_content)

    fs_commands.cat('test.txt')
    captured = capsys.readouterr()
    assert test_content in captured.out


def test_cat_nonexistent_file(fs_commands, capsys):
    """Тест команды cat для несуществующего файла."""
    fs_commands.cat('nonexistent.txt')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_cat_directory(fs_commands, temp_dir, capsys):
    """Тест команды cat для директории (должна выдать ошибку)."""
    subdir = temp_dir / 'subdir'
    subdir.mkdir()

    fs_commands.cat('subdir')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_cp_file_success(fs_commands, temp_dir):
    """Тест успешного копирования файла."""
    src = temp_dir / 'source.txt'
    dst = temp_dir / 'dest.txt'

    src.touch()
    fs_commands.cp('source.txt', 'dest.txt')

    assert dst.exists()
    assert src.exists()


def test_cp_directory_without_recursive(fs_commands, temp_dir, capsys):
    """Тест копирования директории без опции -r."""
    src = temp_dir / 'source_dir'
    src.mkdir()

    fs_commands.cp('source_dir', 'dest_dir')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_cp_directory_with_recursive(fs_commands, temp_dir):
    """Тест рекурсивного копирования директории."""
    src = temp_dir / 'source_dir'
    src.mkdir()
    (src / 'file.txt').touch()

    fs_commands.cp('source_dir', 'dest_dir', recursive=True)
    assert (temp_dir / 'dest_dir').exists()
    assert (temp_dir / 'dest_dir' / 'file.txt').exists()


def test_mv_file_success(fs_commands, temp_dir):
    """Тест успешного перемещения файла."""
    src = temp_dir / 'source.txt'
    dst = temp_dir / 'dest.txt'

    src.touch()
    fs_commands.mv('source.txt', 'dest.txt')

    assert not src.exists()
    assert dst.exists()


def test_mv_nonexistent_file(fs_commands, capsys):
    """Тест перемещения несуществующего файла."""
    fs_commands.mv('nonexistent.txt', 'dest.txt')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_rm_file_success(fs_commands, temp_dir):
    """Тест успешного удаления файла."""
    test_file = temp_dir / 'test.txt'
    test_file.touch()

    fs_commands.rm('test.txt')

    assert not test_file.exists()
    assert (temp_dir / '.trash' / 'test.txt').exists()


def test_rm_directory_without_recursive(fs_commands, temp_dir, capsys):
    """Тест удаления директории без опции -r."""
    test_dir = temp_dir / 'testdir'
    test_dir.mkdir()

    fs_commands.rm('testdir')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_pwd(fs_commands, temp_dir, capsys):
    """Тест команды pwd."""
    fs_commands.pwd()
    captured = capsys.readouterr()
    assert str(temp_dir) in captured.out
