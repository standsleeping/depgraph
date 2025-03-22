import pytest
from depgraph.import_crawler.package_searcher import (
    get_ancestor_paths,
    find_module_in_package_hierarchy,
)


@pytest.fixture
def nested_package_structure(tmp_path):
    """
    Creates a nested package structure for testing:

    tmp_path/
    ├── root_pkg/
    │   ├── __init__.py
    │   ├── utils.py
    │   ├── views.render.py
    │   └── subpkg/
    │       ├── __init__.py
    │       ├── mid_utils.py
    │       └── deep/
    │           ├── __init__.py
    │           └── module.py
    """
    root_pkg = tmp_path / "root_pkg"
    subpkg = root_pkg / "subpkg"
    deep_pkg = subpkg / "deep"

    # Create directories
    for dir_path in [root_pkg, subpkg, deep_pkg]:
        dir_path.mkdir(parents=True)
        (dir_path / "__init__.py").touch()

    # Create module files
    (root_pkg / "utils.py").touch()
    (root_pkg / "views.render.py").touch()
    (subpkg / "mid_utils.py").touch()
    (deep_pkg / "module.py").touch()

    return tmp_path


def test_get_ancestor_paths(nested_package_structure):
    """Returns correct list of ancestor paths."""
    deep_dir = nested_package_structure / "root_pkg/subpkg/deep"
    root_dir = nested_package_structure / "root_pkg"

    paths = get_ancestor_paths(deep_dir, root_dir)

    expected = [
        deep_dir.resolve(),
        deep_dir.parent.resolve(),  # subpkg
        deep_dir.parent.parent.resolve(),  # root_pkg
    ]

    assert paths == expected


def test_get_ancestor_paths_same_dir(nested_package_structure):
    """Returns single path when start and root are the same."""
    root_dir = nested_package_structure / "root_pkg"

    paths = get_ancestor_paths(root_dir, root_dir)

    assert paths == [root_dir.resolve()]


def test_find_module_direct_file(nested_package_structure):
    """Finds module as a direct .py file."""
    deep_dir = nested_package_structure / "root_pkg/subpkg/deep"
    root_dir = nested_package_structure / "root_pkg"

    result = find_module_in_package_hierarchy("utils", deep_dir, root_dir)

    assert result == root_dir / "utils.py"


def test_find_module_as_package(nested_package_structure):
    """Finds module as a package with __init__.py."""
    deep_dir = nested_package_structure / "root_pkg/subpkg/deep"
    root_dir = nested_package_structure / "root_pkg"

    result = find_module_in_package_hierarchy("subpkg", deep_dir, root_dir)

    assert result == root_dir / "subpkg" / "__init__.py"


def test_find_module_dotted_filename(nested_package_structure):
    """Finds module with dots in the filename."""
    deep_dir = nested_package_structure / "root_pkg/subpkg/deep"
    root_dir = nested_package_structure / "root_pkg"

    result = find_module_in_package_hierarchy("views.render", deep_dir, root_dir)

    assert result == root_dir / "views.render.py"


def test_find_module_nonexistent(nested_package_structure):
    """Returns None for nonexistent modules."""
    deep_dir = nested_package_structure / "root_pkg/subpkg/deep"
    root_dir = nested_package_structure / "root_pkg"

    result = find_module_in_package_hierarchy("nonexistent", deep_dir, root_dir)

    assert result is None


def test_find_module_in_middle_package(nested_package_structure):
    """Finds module in a middle-level package."""
    deep_dir = nested_package_structure / "root_pkg/subpkg/deep"
    root_dir = nested_package_structure / "root_pkg"

    result = find_module_in_package_hierarchy("mid_utils", deep_dir, root_dir)

    assert result == root_dir / "subpkg" / "mid_utils.py"
