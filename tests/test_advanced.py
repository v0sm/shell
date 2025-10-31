"""Тесты для продвинутых команд."""

import pytest


@pytest.fixture
def temp_dir(tmp_path):
    """Создание временной директории для тестов."""
    return tmp_path

def test_grep_find_in_file(advanced_commands, temp_dir, capsys):
    """Тест поиска паттерна в файле."""
    test_file = temp_dir / 'test.txt'
    test_file.write_text('Hello World\nTest Line\nAnother Line')

    advanced_commands.grep('World', 'test.txt')
    captured = capsys.readouterr()
    assert 'World' in captured.out


def test_grep_not_found(advanced_commands, temp_dir, capsys):
    """Тест поиска несуществующего паттерна."""
    test_file = temp_dir / 'test.txt'
    test_file.write_text('Hello World')

    advanced_commands.grep('NonExistent', 'test.txt')
    captured = capsys.readouterr()
    assert 'No matches found' in captured.out


def test_grep_recursive(advanced_commands, temp_dir, capsys):
    """Тест рекурсивного поиска."""
    subdir = temp_dir / 'subdir'
    subdir.mkdir()
    (subdir / 'file.txt').write_text('Pattern here')

    advanced_commands.grep('Pattern', '.', recursive=True)
    captured = capsys.readouterr()
    assert 'Pattern' in captured.out


def test_grep_ignore_case(advanced_commands, temp_dir, capsys):
    """Тест поиска без учёта регистра."""
    test_file = temp_dir / 'test.txt'
    test_file.write_text('UPPERCASE text')

    advanced_commands.grep('uppercase', 'test.txt', ignore_case=True)
    captured = capsys.readouterr()
    assert 'UPPERCASE' in captured.out


def test_grep_nonexistent_path(advanced_commands, capsys):
    """Тест поиска в несуществующем пути."""
    advanced_commands.grep('pattern', '/nonexistent/path')
    captured = capsys.readouterr()
    assert 'Error' in captured.out


def test_history_empty(advanced_commands, capsys):
    """Тест отображения пустой истории."""
    advanced_commands.show_history()
    captured = capsys.readouterr()
    assert 'Command History' in captured.out


def test_history_with_commands(advanced_commands, capsys):
    """Тест отображения истории с командами."""
    advanced_commands.add_to_history('ls')
    advanced_commands.add_to_history('cd /tmp')

    advanced_commands.show_history()
    captured = capsys.readouterr()
    assert 'ls' in captured.out
    assert 'cd /tmp' in captured.out


def test_undo_no_commands(advanced_commands, capsys):
    """Тест undo когда нет команд для отмены."""
    advanced_commands.undo()
    captured = capsys.readouterr()
    assert 'Nothing to undo' in captured.out


def test_undo_cp_command(advanced_commands, temp_dir):
    """Тест отмены команды cp."""
    src = temp_dir / 'source.txt'
    dst = temp_dir / 'dest.txt'
    src.touch()

    advanced_commands.history.append(f"cp|{src}|{dst}")
    dst.touch()

    advanced_commands.undo()

    assert not dst.exists()


def test_undo_mv_command(advanced_commands, temp_dir):
    """Тест отмены команды mv."""
    src = temp_dir / 'source.txt'
    dst = temp_dir / 'dest.txt'

    dst.touch()

    advanced_commands.history.append(f"mv|{src}|{dst}")

    advanced_commands.undo()

    assert src.exists()
    assert not dst.exists()


def test_undo_rm_command(advanced_commands, temp_dir):
    """Тест отмены команды rm."""
    original = temp_dir / 'file.txt'
    trash = temp_dir / '.trash' / 'file.txt'
    trash.parent.mkdir(exist_ok=True)

    trash.touch()

    advanced_commands.history.append(f"rm|{original}|{trash}")

    advanced_commands.undo()

    assert original.exists()
    assert not trash.exists()
