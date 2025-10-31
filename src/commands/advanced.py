"""Продвинутые команды: grep, history, undo."""

import os
import shutil
import re
from typing import Pattern

from .base import BaseCommands
from ..constants import ERROR_PATH_NOT_FOUND, SEPARATOR_SHORT


class AdvancedCommands(BaseCommands):
    """Класс с продвинутыми командами."""

    def grep(self, pattern: str, path: str, recursive: bool = False,
             ignore_case: bool = False) -> None:
        """
        Команда grep - поиск по содержимому файлов.

        Args:
            pattern: Шаблон для поиска
            path: Путь для поиска
            recursive: Рекурсивный поиск
            ignore_case: Игнорировать регистр
        """
        try:
            search_path = os.path.abspath(os.path.join(self.current_dir, path))

            if not os.path.exists(search_path):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {search_path}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {search_path}")
                return

            flags = re.IGNORECASE if ignore_case else 0
            regex = re.compile(pattern, flags)

            found = False

            if os.path.isfile(search_path):
                found = self._grep_file(search_path, regex)
            elif os.path.isdir(search_path):
                if recursive:
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if self._grep_file(file_path, regex):
                                found = True
                else:
                    for item in os.listdir(search_path):
                        file_path = os.path.join(search_path, item)
                        if os.path.isfile(file_path):
                            if self._grep_file(file_path, regex):
                                found = True

            if not found:
                print(f"No matches found for pattern: {pattern}")

            self.logger.log_success(f"grep {pattern} {search_path}")

        except Exception as e:
            self.logger.log_error(f"grep failed: {e}")
            print(f"Error: {e}")

    def _grep_file(self, file_path: str, regex: Pattern) -> bool:
        """
        Вспомогательная функция для поиска в файле.

        Args:
            file_path: Путь к файлу
            regex: Скомпилированное регулярное выражение

        Returns:
            True если найдены совпадения, False иначе
        """
        found = False
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if regex.search(line):
                        print(f"{file_path}:{line_num}: {line.rstrip()}")
                        found = True
        except Exception:
            pass
        return found

    def show_history(self) -> None:
        """Команда history - показать историю команд."""
        try:
            print("Command History (last 100 commands):")
            print(SEPARATOR_SHORT)
            for i, cmd in enumerate(self.history[-100:], 1):
                if '|' not in cmd or not cmd.startswith(('cp|', 'mv|', 'rm|')):
                    print(f"{i}: {cmd}")

            self.logger.log_success("history")

        except Exception as e:
            self.logger.log_error(f"history failed: {e}")
            print(f"Error: {e}")

    def undo(self) -> None:
        """Команда undo - отмена последней операции."""
        try:
            for i in range(len(self.history) - 1, -1, -1):
                cmd = self.history[i]
                if '|' in cmd:
                    parts = cmd.split('|')
                    cmd_type = parts[0]

                    if cmd_type == 'cp':
                        dst = parts[2]
                        if os.path.exists(dst):
                            if os.path.isdir(dst):
                                shutil.rmtree(dst)
                            else:
                                os.remove(dst)
                            print(f"Undone: removed copied file/folder {dst}")
                            self.logger.log_success(f"undo cp: removed {dst}")
                        else:
                            print(f"Cannot undo: {dst} not found")

                    elif cmd_type == 'mv':
                        src = parts[1]
                        dst = parts[2]
                        if os.path.exists(dst):
                            shutil.move(dst, src)
                            print(f"Undone: moved back {dst} -> {src}")
                            self.logger.log_success(f"undo mv: {dst} -> {src}")
                        else:
                            print(f"Cannot undo: {dst} not found")

                    elif cmd_type == 'rm':
                        original = parts[1]
                        trash = parts[2]
                        if os.path.exists(trash):
                            shutil.move(trash, original)
                            print(f"Undone: restored {original}")
                            self.logger.log_success(f"undo rm: restored {original}")
                        else:
                            print(f"Cannot undo: {trash} not found in trash")

                    self.history.pop(i)
                    self.save_history()
                    return

            print("Nothing to undo")

        except Exception as e:
            self.logger.log_error(f"undo failed: {e}")
            print(f"Error: {e}")
