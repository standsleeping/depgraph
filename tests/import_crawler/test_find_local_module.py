import pytest
from depgraph.import_crawler.find_local_module import find_local_module
import os


@pytest.fixture
def module_finder(tmp_path):
    """Returns a tuple of (search_dir, stdlib_paths, project_root)."""
    stdlib_paths = ["/usr/lib/python3.8", "/usr/local/lib/python3.8"]
    return str(tmp_path), stdlib_paths, str(tmp_path)


def test_find_single_file_module(module_finder):
    """Simple 'modulename.py' module files are found."""
    search_dir, stdlib_paths, project_root = module_finder
    module = os.path.join(search_dir, "mymodule.py")
    open(module, "w").close()

    result = find_local_module(
        "mymodule",
        search_dir,
        stdlib_paths,
        project_root,
    )

    assert result == module


def test_find_package_module(module_finder):
    """Modules within packages are found."""
    search_dir, stdlib_paths, project_root = module_finder
    package_dir = os.path.join(search_dir, "mypackage")
    os.makedirs(package_dir)

    init_file = os.path.join(package_dir, "__init__.py")
    open(init_file, "w").close()

    result = find_local_module(
        "mypackage",
        search_dir,
        stdlib_paths,
        project_root,
    )

    assert result == init_file


def test_find_submodule(module_finder):
    """Submodules are found using dot notation."""
    search_dir, stdlib_paths, project_root = module_finder
    package_dir = os.path.join(search_dir, "mypackage")
    os.makedirs(package_dir)

    submodule = os.path.join(package_dir, "submodule.py")

    open(submodule, "w").close()

    result = find_local_module(
        "mypackage.submodule",
        search_dir,
        stdlib_paths,
        project_root,
    )

    assert result == submodule


def test_nonexistent_module(module_finder):
    """Nonexistent modules return None."""
    search_dir, stdlib_paths, project_root = module_finder

    result = find_local_module(
        "nonexistent",
        search_dir,
        stdlib_paths,
        project_root,
    )

    assert result is None


def test_nested_package_structure(module_finder):
    """Modules in nested package structures are found."""
    search_dir, stdlib_paths, project_root = module_finder
    pkg_dir = os.path.join(search_dir, "pkg")
    subpkg_dir = os.path.join(pkg_dir, "subpkg")
    os.makedirs(subpkg_dir)

    module_file = os.path.join(subpkg_dir, "module.py")
    open(module_file, "w").close()

    result = find_local_module(
        "pkg.subpkg.module",
        search_dir,
        stdlib_paths,
        project_root,
    )

    assert result == module_file


def test_prefer_file_over_package(module_finder):
    """Single 'modulename.py' files are preferred over packages with the same name."""
    search_dir, stdlib_paths, project_root = module_finder
    module_file = os.path.join(search_dir, "module.py")
    open(module_file, "w").close()

    module_dir = os.path.join(search_dir, "module")
    os.makedirs(module_dir)
    init_file = os.path.join(module_dir, "__init__.py")
    open(init_file, "w").close()

    result = find_local_module(
        "module",
        search_dir,
        stdlib_paths,
        project_root,
    )

    assert result == module_file


def test_empty_module_name(module_finder):
    """Empty module names return None."""
    search_dir, stdlib_paths, project_root = module_finder

    result = find_local_module(
        "",
        search_dir,
        stdlib_paths,
        project_root,
    )

    assert result is None
