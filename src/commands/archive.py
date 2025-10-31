"""Команды для работы с архивами."""

import os
import zipfile
import tarfile

from .base import BaseCommands
from ..constants import (
    ERROR_PATH_NOT_FOUND,
    SUCCESS_CREATED_ARCHIVE,
    SUCCESS_EXTRACTED_ARCHIVE
)


class ArchiveCommands(BaseCommands):
    """Класс с командами для работы с архивами."""

    def zip_folder(self, folder: str, archive_name: str) -> None:
        """
        Команда zip - создание ZIP архива.

        Args:
            folder: Путь к папке для архивирования
            archive_name: Имя создаваемого архива
        """
        try:
            folder_path = os.path.abspath(os.path.join(self.current_dir, folder))
            archive_path = os.path.abspath(os.path.join(self.current_dir, archive_name))

            if not os.path.exists(folder_path):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {folder_path}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {folder_path}")
                return

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(folder_path):
                    zipf.write(folder_path, os.path.basename(folder_path))
                else:
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                            zipf.write(file_path, arcname)

            print(f"{SUCCESS_CREATED_ARCHIVE}: {archive_path}")
            self.logger.log_success(f"zip {folder_path} {archive_path}")

        except Exception as e:
            self.logger.log_error(f"zip failed: {e}")
            print(f"Error: {e}")

    def unzip_archive(self, archive_name: str) -> None:
        """
        Команда unzip - распаковка ZIP архива.

        Args:
            archive_name: Имя архива для распаковки
        """
        try:
            archive_path = os.path.abspath(os.path.join(self.current_dir, archive_name))

            if not os.path.exists(archive_path):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {archive_path}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {archive_path}")
                return

            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(self.current_dir)

            print(f"{SUCCESS_EXTRACTED_ARCHIVE}: {archive_path}")
            self.logger.log_success(f"unzip {archive_path}")

        except Exception as e:
            self.logger.log_error(f"unzip failed: {e}")
            print(f"Error: {e}")

    def tar_folder(self, folder: str, archive_name: str) -> None:
        """
        Команда tar - создание TAR.GZ архива.

        Args:
            folder: Путь к папке для архивирования
            archive_name: Имя создаваемого архива
        """
        try:
            folder_path = os.path.abspath(os.path.join(self.current_dir, folder))
            archive_path = os.path.abspath(os.path.join(self.current_dir, archive_name))

            if not os.path.exists(folder_path):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {folder_path}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {folder_path}")
                return

            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(folder_path, arcname=os.path.basename(folder_path))

            print(f"{SUCCESS_CREATED_ARCHIVE}: {archive_path}")
            self.logger.log_success(f"tar {folder_path} {archive_path}")

        except Exception as e:
            self.logger.log_error(f"tar failed: {e}")
            print(f"Error: {e}")

    def untar_archive(self, archive_name: str) -> None:
        """
        Команда untar - распаковка TAR.GZ архива.

        Args:
            archive_name: Имя архива для распаковки
        """
        try:
            archive_path = os.path.abspath(os.path.join(self.current_dir, archive_name))

            if not os.path.exists(archive_path):
                self.logger.log_error(f"{ERROR_PATH_NOT_FOUND}: {archive_path}")
                print(f"Error: {ERROR_PATH_NOT_FOUND}: {archive_path}")
                return

            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(self.current_dir, filter='data')

            print(f"{SUCCESS_EXTRACTED_ARCHIVE}: {archive_path}")
            self.logger.log_success(f"untar {archive_path}")

        except Exception as e:
            self.logger.log_error(f"untar failed: {e}")
            print(f"Error: {e}")
