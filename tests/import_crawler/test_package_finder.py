import os
import pytest
from depgraph.import_crawler.package_finder import find_outermost_package_root


@pytest.fixture
def temp_project_structure(tmp_path):
    """
    Creates a temporary project structure for testing:

    tmp_path/
    ├── outer_pkg/
    │   ├── __init__.py
    │   ├── middle_pkg/
    │   │   ├── __init__.py
    │   │   └── inner_pkg/
    │   │       ├── __init__.py
    │   │       └── module.py
    │   └── sibling_pkg/
    │       └── other.py
    └── not_a_pkg/
        └── random.txt
    """
    # Create the nested package structure
    outer_pkg = tmp_path / "outer_pkg"
    middle_pkg = outer_pkg / "middle_pkg"
    inner_pkg = middle_pkg / "inner_pkg"
    sibling_pkg = outer_pkg / "sibling_pkg"
    not_a_pkg = tmp_path / "not_a_pkg"

    # Create directories
    for dir_path in [outer_pkg, middle_pkg, inner_pkg, sibling_pkg, not_a_pkg]:
        dir_path.mkdir(parents=True)

    # Create __init__.py files
    for pkg in [outer_pkg, middle_pkg, inner_pkg]:
        (pkg / "__init__.py").touch()

    # Create Python files
    (inner_pkg / "module.py").touch()
    (sibling_pkg / "other.py").touch()

    # Create a non-Python file
    (not_a_pkg / "random.txt").touch()

    return tmp_path


def test_find_package_root_from_inner_module(temp_project_structure):
    """Finds package root starting from an inner module."""
    start_dir = temp_project_structure / "outer_pkg/middle_pkg/inner_pkg"
    result = find_outermost_package_root(str(start_dir))
    assert result == str(temp_project_structure / "outer_pkg")


def test_find_package_root_from_sibling_package(temp_project_structure):
    """Finds package root starting from a sibling package."""
    start_dir = temp_project_structure / "outer_pkg/sibling_pkg"
    result = find_outermost_package_root(str(start_dir))
    assert result == str(temp_project_structure / "outer_pkg")


def test_non_package_directory(temp_project_structure):
    """Finds package root starting from a non-package directory."""
    start_dir = temp_project_structure / "not_a_pkg"
    result = find_outermost_package_root(str(start_dir))
    assert result == str(start_dir)


def test_py_files_no_init(temp_project_structure):
    """Finds root from directory containing .py files but no __init__.py."""
    start_dir = temp_project_structure / "outer_pkg/sibling_pkg"
    result = find_outermost_package_root(str(start_dir))
    assert result == str(temp_project_structure / "outer_pkg")


@pytest.mark.skipif(os.name == "nt", reason="Permission tests unreliable on Windows")
def test_permission_denied(temp_project_structure):
    """Handles permission denied errors."""
    restricted_dir = temp_project_structure / "restricted"
    restricted_dir.mkdir()
    restricted_dir.chmod(0o000)  # Remove permissions

    try:
        start_dir = restricted_dir
        result = find_outermost_package_root(str(start_dir))
        assert result == str(start_dir)
    finally:
        restricted_dir.chmod(0o755)


def test_absolute_path_handling(temp_project_structure):
    """Handles relative paths being converted to absolute paths."""
    start_dir = temp_project_structure / "outer_pkg/middle_pkg"
    result = find_outermost_package_root(str(start_dir))
    assert os.path.isabs(result)
    assert result == str(temp_project_structure / "outer_pkg")
