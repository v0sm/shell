"""Точка входа в shell-эмулятор."""

from .shell import Shell


def main() -> None:
    """Главная функция запуска shell-эмулятора."""
    shell = Shell()
    shell.run()


if __name__ == '__main__':
    main()
