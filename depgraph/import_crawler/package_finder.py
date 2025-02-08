import os
import logging
from ..logger import setup_logger


def find_outermost_package_root(
    start_dir: str, logger: logging.Logger | None = None
) -> str:
    """
    Recursively searches for the outermost Python package/module directory.
    A directory is considered a Python package/module if it:
        1. Contains an __init__.py file, or
        2. Contains any .py files

    Args:
        start_dir: The starting directory path to begin the search from
        logger: Optional logger instance

    Returns:
        The path to the outermost Python package/module directory
    """
    if logger is None:
        logger = setup_logger()

    logger.debug(f"Finding outermost package root starting from: {start_dir}")

    def is_python_dir(dir_path: str) -> bool:
        # Check for __init__.py
        if os.path.exists(os.path.join(dir_path, "__init__.py")):
            return True

        # Check for any .py files
        for file in os.listdir(dir_path):
            if file.endswith(".py"):
                return True
        return False

    current_dir = os.path.abspath(start_dir)
    last_valid_dir = current_dir

    while True:
        parent_dir = os.path.dirname(current_dir)

        # Stop if we reached the root directory
        if parent_dir == current_dir:
            break

        try:
            if is_python_dir(parent_dir):
                last_valid_dir = parent_dir
                current_dir = parent_dir
            else:
                break
        except (PermissionError, FileNotFoundError):
            # Stop if we can't access the directory
            break

    logger.debug(f"Found outermost root: {last_valid_dir}")
    return last_valid_dir
