import pytest
from depgraph.import_crawler.import_crawler import ImportCrawler


def test_find_local_module_first(crawler, tmp_path):
    """Local modules are found before checking sys.path."""
    local_module = tmp_path / "test_module.py"
    local_module.touch()

    result = crawler.find_module("test_module", tmp_path)
    assert result == local_module


def test_fallback_to_syspath(crawler, tmp_path):
    """Falls back to sys.path when local module not found."""
    other_dir = tmp_path / "other"
    other_dir.mkdir()

    module_file = other_dir / "test_module.py"
    module_file.touch()

    with pytest.MonkeyPatch.context() as mp:
        mp.syspath_prepend(str(other_dir))
        result = crawler.find_module("test_module", tmp_path)
        assert result == module_file


def test_nonexistent_module(crawler, tmp_path):
    """Returns None when module is not found anywhere."""
    result = crawler.find_module("nonexistent_module", tmp_path)
    assert result is None


def test_package_module(crawler, tmp_path):
    """Finds modules within packages."""
    package_dir = tmp_path / "mypackage"
    package_dir.mkdir()

    init_file = package_dir / "__init__.py"
    init_file.touch()

    submodule = package_dir / "submodule.py"
    submodule.touch()

    result = crawler.find_module("mypackage.submodule", tmp_path)
    assert result == submodule


def test_non_local_module(crawler, tmp_path):
    """Returns None for non-local modules."""
    # Create a module outside the search directory
    outside_dir = tmp_path.parent / "outside"
    outside_dir.mkdir(exist_ok=True)
    outside_module = outside_dir / "outside_module.py"
    outside_module.touch()

    # Search from tmp_path
    result = crawler.find_module("outside_module", tmp_path)
    assert result is None


def test_relative_path_resolution(crawler, tmp_path):
    """Resolves relative paths correctly."""
    module_dir = tmp_path / "package"
    module_dir.mkdir()

    module_file = module_dir / "test_module.py"
    module_file.touch()

    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(tmp_path)
        result = crawler.find_module("package.test_module", tmp_path)
        assert result == module_file


def test_find_module_with_package_expansion(tmp_path):
    """Expands search to outer package roots."""
    # Create nested package structure
    root_pkg = tmp_path / "root_pkg"
    subpkg = root_pkg / "subpkg"
    deep_pkg = subpkg / "deep"

    for dir_path in [root_pkg, subpkg, deep_pkg]:
        dir_path.mkdir(parents=True)
        (dir_path / "__init__.py").touch()

    # Create target module in root package
    utils_module = root_pkg / "utils.py"
    utils_module.touch()

    # Create a module in the deep package that we'll use as the starting point
    deep_module = deep_pkg / "module.py"
    deep_module.write_text("from ...utils import helper")

    # Initialize crawler with the deep module as the root file
    crawler = ImportCrawler(deep_module)

    # Try to find utils.py from deep inside the package
    result = crawler.find_module("utils", deep_pkg)
    assert result == utils_module


def test_find_module_expansion_not_needed(tmp_path):
    """Doesn't expand search when module is found normally."""
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").touch()

    module_file = pkg_dir / "module.py"
    module_file.touch()

    # Initialize crawler with the module we're looking for
    crawler = ImportCrawler(module_file)

    result = crawler.find_module("module", pkg_dir)
    assert result == module_file


def test_find_module_expansion_fails(tmp_path):
    """Returns None when expansion doesn't help."""
    # Create nested package structure
    root_pkg = tmp_path / "root_pkg"
    subpkg = root_pkg / "subpkg"

    for dir_path in [root_pkg, subpkg]:
        dir_path.mkdir(parents=True)
        (dir_path / "__init__.py").touch()

    # Create a module to initialize the crawler with
    test_module = subpkg / "test.py"
    test_module.touch()

    crawler = ImportCrawler(test_module)

    # Try to find non-existent module
    result = crawler.find_module("nonexistent", subpkg)
    assert result is None


def test_find_module_with_middle_package_expansion(tmp_path):
    """Expands search to middle package for double-dot relative imports."""
    # Create nested package structure
    root_pkg = tmp_path / "root_pkg"
    subpkg = root_pkg / "subpkg"
    deep_pkg = subpkg / "deep"

    for dir_path in [root_pkg, subpkg, deep_pkg]:
        dir_path.mkdir(parents=True)
        (dir_path / "__init__.py").touch()

    # Create target module in middle package (subpkg)
    utils_module = subpkg / "utils.py"
    utils_module.touch()

    # Create a module in the deep package that we'll use as the starting point
    deep_module = deep_pkg / "module.py"
    deep_module.write_text("from ..utils import helper")

    # Initialize crawler with the deep module as the root file
    crawler = ImportCrawler(deep_module)

    # Try to find utils.py from deep inside the package
    result = crawler.find_module("utils", deep_pkg)
    assert result == utils_module


def test_find_module_with_recursive_package_search(tmp_path):
    """Recursively searches through all package levels to find modules."""
    # Create nested package structure
    root_pkg = tmp_path / "root_pkg"
    subpkg1 = root_pkg / "subpkg1"
    subpkg2 = subpkg1 / "subpkg2"
    deep_pkg = subpkg2 / "deep"

    for dir_path in [root_pkg, subpkg1, subpkg2, deep_pkg]:
        dir_path.mkdir(parents=True)
        (dir_path / "__init__.py").touch()

    # Create target modules at different levels
    root_module = root_pkg / "root_utils.py"
    root_module.touch()

    mid_module = subpkg1 / "mid_utils.py"
    mid_module.touch()

    sub_module = subpkg2 / "sub_utils.py"
    sub_module.touch()

    # Create a module in the deepest package that we'll use as the starting point
    deep_module = deep_pkg / "module.py"
    deep_module.write_text(
        "from ...sub_utils import helper\n"
        "from ....mid_utils import other\n"
        "from .....root_utils import thing"
    )

    # Initialize crawler with the deep module as the root file
    crawler = ImportCrawler(deep_module)

    # Try to find each module from deep inside the package
    search_dir = deep_pkg

    assert crawler.find_module("sub_utils", search_dir) == sub_module
    assert crawler.find_module("mid_utils", search_dir) == mid_module
    assert crawler.find_module("root_utils", search_dir) == root_module
