"""Константы для shell-эмулятора."""

# Файлы системы
LOG_FILE: str = 'shell.log'
HISTORY_FILE: str = '.history'
TRASH_DIR: str = '.trash'

# Ограничения
MAX_HISTORY_SIZE: int = 100

# Форматы логов
LOG_FORMAT: str = '[%(asctime)s] %(message)s'
LOG_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

# Сообщения об ошибках
ERROR_PATH_NOT_FOUND: str = "Path not found"
ERROR_NOT_A_DIRECTORY: str = "Not a directory"
ERROR_NOT_A_FILE: str = "Is a directory"
ERROR_SOURCE_NOT_FOUND: str = "Source not found"
ERROR_USE_RECURSIVE: str = "Use -r option to copy/remove directories"
ERROR_CANNOT_REMOVE_ROOT: str = "Cannot remove root or parent directory"
ERROR_UNKNOWN_COMMAND: str = "Unknown command"

# Сообщения об успехе
SUCCESS_COPIED: str = "Copied"
SUCCESS_MOVED: str = "Moved"
SUCCESS_REMOVED: str = "Removed"
SUCCESS_CREATED_ARCHIVE: str = "Created archive"
SUCCESS_EXTRACTED_ARCHIVE: str = "Extracted archive"

# Разделители
SEPARATOR_LINE: str = "-" * 80
SEPARATOR_SHORT: str = "-" * 50
HEADER_SEPARATOR: str = "=" * 60

# Подсказки для пользователя
PROMPT_REMOVE_DIR: str = "Remove directory '{}' and all its contents? (y/n): "
PROMPT_EXIT: str = "Type 'exit' to quit"
