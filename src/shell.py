"""Главный модуль shell-эмулятора."""

from typing import Optional, Tuple, List, Dict

from .logger import ShellLogger
from .commands import ShellCommands
from .constants import HEADER_SEPARATOR, ERROR_UNKNOWN_COMMAND, PROMPT_EXIT


class Shell:
    """Класс shell-эмулятора."""

    def __init__(self) -> None:
        """Инициализация shell."""
        self.logger = ShellLogger()
        self.commands = ShellCommands(self.logger)
        self.running = True

    def parse_command(self, user_input: str) -> Tuple[Optional[str], List[str], Dict[str, bool]]:
        """
        Парсинг введённой команды.

        Args:
            user_input: Строка с командой от пользователя

        Returns:
            Кортеж (команда, аргументы, опции)
        """
        parts = user_input.strip().split()
        if not parts:
            return None, [], {}

        command = parts[0]
        args = []
        options = {}

        i = 1
        while i < len(parts):
            if parts[i].startswith('-'):
                option = parts[i]
                if option == '-l':
                    options['detailed'] = True
                elif option == '-r':
                    options['recursive'] = True
                elif option == '-i':
                    options['ignore_case'] = True
            else:
                args.append(parts[i])
            i += 1

        return command, args, options

    def execute_command(self, user_input: str) -> None:
        """
        Выполнение команды.

        Args:
            user_input: Введённая пользователем строка
        """
        command, args, options = self.parse_command(user_input)

        if not command:
            return

        self.logger.log_command(user_input)

        if command not in ['history', 'undo']:
            self.commands.add_to_history(user_input)

        if command == 'ls':
            path = args[0] if args else None
            self.commands.ls(path, options.get('detailed', False))

        elif command == 'cd':
            if not args:
                print("Error: cd requires a path argument")
                return
            self.commands.cd(args[0])

        elif command == 'cat':
            if not args:
                print("Error: cat requires a file path")
                return
            self.commands.cat(args[0])

        elif command == 'cp':
            if len(args) < 2:
                print("Error: cp requires source and destination")
                return
            self.commands.cp(args[0], args[1], options.get('recursive', False))

        elif command == 'mv':
            if len(args) < 2:
                print("Error: mv requires source and destination")
                return
            self.commands.mv(args[0], args[1])

        elif command == 'rm':
            if not args:
                print("Error: rm requires a path")
                return
            self.commands.rm(args[0], options.get('recursive', False))

        elif command == 'zip':
            if len(args) < 2:
                print("Error: zip requires folder and archive name")
                return
            self.commands.zip_folder(args[0], args[1])

        elif command == 'unzip':
            if not args:
                print("Error: unzip requires archive name")
                return
            self.commands.unzip_archive(args[0])

        elif command == 'tar':
            if len(args) < 2:
                print("Error: tar requires folder and archive name")
                return
            self.commands.tar_folder(args[0], args[1])

        elif command == 'untar':
            if not args:
                print("Error: untar requires archive name")
                return
            self.commands.untar_archive(args[0])

        elif command == 'grep':
            if len(args) < 2:
                print("Error: grep requires pattern and path")
                return
            self.commands.grep(args[0], args[1],
                               options.get('recursive', False),
                               options.get('ignore_case', False))

        elif command == 'history':
            self.commands.show_history()

        elif command == 'undo':
            self.commands.undo()

        elif command == 'pwd':
            self.commands.pwd()

        elif command == 'exit':
            print("bb!")
            self.running = False

        else:
            print(f"{ERROR_UNKNOWN_COMMAND}: {command}")
            self.logger.log_error(f"{ERROR_UNKNOWN_COMMAND}: {command}")

    def run(self) -> None:
        """Главный цикл shell."""
        print(HEADER_SEPARATOR)
        print("Shell Emulator")
        print(PROMPT_EXIT)
        print(HEADER_SEPARATOR)

        while self.running:
            try:
                prompt = f"{self.commands.current_dir}> "
                user_input = input(prompt)

                if user_input.strip():
                    self.execute_command(user_input)

            except KeyboardInterrupt:
                print(f"\n{PROMPT_EXIT}")
            except EOFError:
                print("\nbb!")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.logger.log_error(str(e))
