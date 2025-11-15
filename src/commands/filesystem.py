"""Команды для работы с файловой системой."""

import os
import shutil
import stat
from datetime import datetime
from typing import Optional

from .base import BaseCommands
from ..constants import (
    ERROR_PATH_NOT_FOUND, ERROR_NOT_A_DIRECTORY, ERROR_NOT_A_FILE,
    ERROR_SOURCE_NOT_FOUND, ERROR_USE_RECURSIVE, ERROR_CANNOT_REMOVE_ROOT,
    SUCCESS_COPIED, SUCCESS_MOVED, SUCCESS_REMOVED, SEPARATOR_LINE
)


class FileSystemCommands(BaseCommands):
    """Класс с командами для работы с файловой системой."""

    def ls(self, path: Optional[str] = None, detailed: bool = False) -> None:
        """
        Команда ls - список файлов и каталогов.

        Args:
            path: Путь к директории (по умолчанию текущая)
            detailed: Показывать ли подробную информацию
        """
        try:
            target_path = path if path else self.current_dir
            target_path = os.path.abspath(os.path.expanduser(target_path))

            if not os.path.exists(target_path):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {target_path}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {target_path}")
                return

            if not os.path.isdir(target_path):
                self.logger.log_error(f"{ERROR_NOT_A_DIRECTORY}: {target_path}")
                print(f"Error: {ERROR_NOT_A_DIRECTORY}: {target_path}")
                return

            items = os.listdir(target_path)

            if detailed:
                print(f"{'Name':<30} {'Size':<15} {'Modified':<20} {'Permissions':<12}")
                print(SEPARATOR_LINE)
                for item in sorted(items):
                    item_path = os.path.join(target_path, item)
                    stats = os.stat(item_path)
                    size = stats.st_size
                    modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    perms = stat.filemode(stats.st_mode)
                    item_type = '[DIR]' if os.path.isdir(item_path) else ''
                    print(f"{item:<30} {size:<15} {modified:<20} {perms:<12} {item_type}")
            else:
                for item in sorted(items, key=str.lower):
                    print(item)

            self.logger.log_success(f"ls {'-l' if detailed else ''} {target_path}")

        except Exception as e:
            self.logger.log_error(f"ls failed: {e}")
            print(f"Error: {e}")

    def cd(self, path: str) -> None:
        """
        Команда cd - смена текущего каталога.

        Args:
            path: Путь к новой директории
        """
        try:
            resolved_path = self.resolve_path(path)

            if not os.path.exists(resolved_path):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {resolved_path}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {resolved_path}")
                return

            if not os.path.isdir(resolved_path):
                self.logger.log_error(f"{ERROR_NOT_A_DIRECTORY}: {resolved_path}")
                print(f"Error: {ERROR_NOT_A_DIRECTORY}: {resolved_path}")
                return

            self.current_dir = resolved_path
            os.chdir(resolved_path)
            print(f"Changed directory to: {self.current_dir}")
            self.logger.log_success(f"cd {resolved_path}")

        except Exception as e:
            self.logger.log_error(f"cd failed: {e}")
            print(f"Error: {e}")

    def cat(self, file_path: str) -> None:
        """
        Команда cat - вывод содержимого файла.

        Args:
            file_path: Путь к файлу
        """
        try:
            full_path = os.path.abspath(os.path.join(self.current_dir, file_path))

            if not os.path.exists(full_path):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {full_path}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {full_path}")
                return

            if os.path.isdir(full_path):
                self.logger.log_error(f"{ERROR_NOT_A_FILE}: {full_path}")
                print(f"Error: {ERROR_NOT_A_FILE}: {full_path}")
                return

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)

            self.logger.log_success(f"cat {full_path}")

        except Exception as e:
            self.logger.log_error(f"cat failed: {e}")
            print(f"Error: {e}")

    def cp(self, source: str, destination: str, recursive: bool = False) -> None:
        """
        Команда cp - копирование файлов/каталогов.

        Args:
            source: Путь к источнику
            destination: Путь назначения
            recursive: Рекурсивное копирование
        """
        try:
            src = os.path.abspath(os.path.join(self.current_dir, source))
            dst = os.path.abspath(os.path.join(self.current_dir, destination))

            if not os.path.exists(src):
                self.logger.log_error(f"{ERROR_SOURCE_NOT_FOUND}: {src}")
                print(f"Error: {ERROR_SOURCE_NOT_FOUND}: {src}")
                return

            if os.path.isdir(src):
                if not recursive:
                    self.logger.log_error(ERROR_USE_RECURSIVE)
                    print(f"Error: {ERROR_USE_RECURSIVE}")
                    return
                shutil.copytree(src, dst)
            else:
                if os.path.isdir(dst):
                    dst = os.path.join(dst, os.path.basename(src))
                shutil.copy2(src, dst)

            undo_info = f"cp|{src}|{dst}"
            self.history.append(undo_info)

            print(f"{SUCCESS_COPIED}: {src} -> {dst}")
            self.logger.log_success(f"cp {'-r' if recursive else ''} {src} {dst}")

        except Exception as e:
            self.logger.log_error(f"cp failed: {e}")
            print(f"Error: {e}")

    def mv(self, source: str, destination: str) -> None:
        """
        Команда mv - перемещение/переименование.

        Args:
            source: Путь к источнику
            destination: Путь назначения
        """
        try:
            src = os.path.abspath(os.path.join(self.current_dir, source))
            dst = os.path.abspath(os.path.join(self.current_dir, destination))

            if not os.path.exists(src):
                self.logger.log_error(f"{ERROR_SOURCE_NOT_FOUND}: {src}")
                print(f"Error: {ERROR_SOURCE_NOT_FOUND}: {src}")
                return

            undo_info = f"mv|{src}|{dst}"
            self.history.append(undo_info)

            shutil.move(src, dst)
            print(f"{SUCCESS_MOVED}: {src} -> {dst}")
            self.logger.log_success(f"mv {src} {dst}")

        except Exception as e:
            self.logger.log_error(f"mv failed: {e}")
            print(f"Error: {e}")

    def rm(self, path: str, recursive: bool = False) -> None:
        """
        Команда rm - удаление файлов/каталогов.

        Args:
            path: Путь к файлу/директории
            recursive: Рекурсивное удаление
        """
        try:
            target = os.path.abspath(os.path.join(self.current_dir, path))

            if target in ['/', '..'] or target == os.path.dirname(self.current_dir):
                self.logger.log_error(ERROR_CANNOT_REMOVE_ROOT)
                print(f"Error: {ERROR_CANNOT_REMOVE_ROOT}")
                return

            if not os.path.exists(target):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {target}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {target}")
                return

            if os.path.isdir(target):
                if not recursive:
                    self.logger.log_error(ERROR_USE_RECURSIVE)
                    print(f"Error: {ERROR_USE_RECURSIVE}")
                    return

                confirm = input(f"Remove directory '{target}' and all its contents? (y/n): ")
                if confirm.lower() != 'y':
                    print("Cancelled")
                    return

            trash_dir_path = os.path.join(self.current_dir, self.trash_dir)
            if not os.path.exists(trash_dir_path):
                os.makedirs(trash_dir_path)

            trash_path = os.path.join(self.trash_dir, os.path.basename(target))
            if os.path.exists(trash_path):
                import time
                timestamp = int(time.time())
                trash_path = f"{trash_path}.{timestamp}"
            shutil.move(target, trash_path)

            undo_info = f"rm|{target}|{trash_path}"
            self.history.append(undo_info)

            print(f"{SUCCESS_REMOVED}: {target}")
            self.logger.log_success(f"rm {'-r' if recursive else ''} {target}")

        except Exception as e:
            self.logger.log_error(f"rm failed: {e}")
            print(f"Error: {e}")

    def pwd(self) -> None:
        """Команда pwd - показать текущую директорию."""
        print(self.current_dir)
        self.logger.log_success(f"pwd: {self.current_dir}")
