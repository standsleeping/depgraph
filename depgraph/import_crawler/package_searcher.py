import os
from typing import Optional, List
import logging
from ..logger import setup_logger


def get_ancestor_paths(start_dir: str, outer_root: str) -> List[str]:
    """Returns a list of all ancestor directory paths from start_dir up to outer_root."""
    paths = []
    current = os.path.abspath(start_dir)
    outer_root = os.path.abspath(outer_root)

    while True:
        paths.append(current)
        if current == outer_root or len(current) < len(outer_root):
            break
        current = os.path.dirname(current)

    return paths


def find_module_in_package_hierarchy(
    module_name: str,
    start_dir: str,
    outer_root: str,
    logger: Optional[logging.Logger] = None,
) -> Optional[str]:
    """
    Searches for a module through the package hierarchy by checking each ancestor directory.

    Args:
        module_name: Name of the module to find (can be dotted)
        start_dir: Directory to start searching from
        outer_root: Outermost package root directory
        logger: Optional logger instance
    """
    if logger is None:
        logger = setup_logger()

    logger.debug(f"Searching for {module_name} from {start_dir} up to {outer_root}")

    # Get all possible directory paths to search
    search_paths = get_ancestor_paths(start_dir, outer_root)

    # For each path, try to find the module
    for path in search_paths:
        # Try as a direct .py file
        module_file = os.path.join(path, module_name + ".py")
        if os.path.isfile(module_file):
            logger.debug(f"Found module file: {module_file}")
            return module_file

        # Try as a package
        package_init = os.path.join(path, module_name, "__init__.py")
        if os.path.isfile(package_init):
            logger.debug(f"Found package: {package_init}")
            return package_init

        # Try as a dotted file (for cases like views.render_html.py)
        if "." in module_name:
            module_parts = module_name.split(".")
            # Try each possible combination of dots vs directories
            for i in range(len(module_parts)):
                file_part = ".".join(module_parts[i:]) + ".py"
                dir_part = os.path.join(*module_parts[:i]) if i > 0 else ""
                full_path = os.path.join(path, dir_part, file_part)
                if os.path.isfile(full_path):
                    logger.debug(f"Found dotted module: {full_path}")
                    return full_path

    logger.debug(f"Module {module_name} not found in hierarchy")
    return None
