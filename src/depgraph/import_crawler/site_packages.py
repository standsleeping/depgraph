import os
import sysconfig
import logging
from typing import Set


def find_project_site_packages(project_root: str, logger: logging.Logger) -> Set[str]:
    """
    Find site-packages directories associated with the project being analyzed.
    Searches from project root upwards until finding Python environment markers.

    Args:
        project_root: Root directory of the project to analyze
        logger: Logger instance for debug output

    Returns:
        Set of absolute paths to site-packages directories
    """
    site_packages = set()
    current_dir = project_root

    while True:
        # Virtual environment markers
        venv_markers = [
            os.path.join(current_dir, "venv"),
            os.path.join(current_dir, ".venv"),
            os.path.join(current_dir, "env"),
            os.path.join(current_dir, ".env"),
        ]

        # Project markers
        project_markers = [
            os.path.join(current_dir, "pyproject.toml"),
            os.path.join(current_dir, "requirements.txt"),
        ]

        # Check virtual environment site-packages
        for venv_dir in venv_markers:
            if os.path.isdir(venv_dir):
                # Look for lib/pythonX.Y/site-packages
                lib_dir = os.path.join(venv_dir, "lib")
                if os.path.isdir(lib_dir):
                    for item in os.listdir(lib_dir):
                        if item.startswith("python"):
                            site_pkg = os.path.join(lib_dir, item, "site-packages")
                            if os.path.isdir(site_pkg):
                                site_packages.add(os.path.abspath(site_pkg))

        # If we found any project markers, stop searching upward
        if any(os.path.exists(marker) for marker in project_markers):
            break

        # Move up one directory
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached root directory
            break
        current_dir = parent_dir

    # If no environment-specific paths found, fall back to system site-packages
    if not site_packages:
        paths = sysconfig.get_paths()
        site_packages = {
            os.path.abspath(p) for p in paths.values() if "site-packages" in p
        }

    logger.debug(f"Found site-packages paths: {site_packages}")
    return site_packages 