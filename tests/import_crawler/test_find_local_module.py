def test_find_single_file_module(crawler, tmp_path):
    """Simple 'modulename.py' module files are found."""
    module = tmp_path / "mymodule.py"
    module.touch()

    result = crawler.find_local_module("mymodule", str(tmp_path))
    assert result == str(module)


def test_find_package_module(crawler, tmp_path):
    """Modules within packages are found."""
    package_dir = tmp_path / "mypackage"
    package_dir.mkdir()

    init_file = package_dir / "__init__.py"
    init_file.touch()

    result = crawler.find_local_module("mypackage", str(tmp_path))
    assert result == str(init_file)


def test_find_submodule(crawler, tmp_path):
    """Submodules are found using dot notation."""
    package_dir = tmp_path / "mypackage"
    package_dir.mkdir()

    submodule = package_dir / "submodule.py"
    submodule.touch()

    result = crawler.find_local_module("mypackage.submodule", str(tmp_path))
    assert result == str(submodule)


def test_nonexistent_module(crawler, tmp_path):
    """Nonexistent modules return None."""
    result = crawler.find_local_module("nonexistent", str(tmp_path))
    assert result is None


def test_non_local_module(crawler, tmp_path):
    """Non-local modules return None."""
    outside_dir = tmp_path.parent / "outside"
    outside_dir.mkdir(exist_ok=True)

    outside_module = outside_dir / "outside_module.py"
    outside_module.touch()

    result = crawler.find_local_module("outside_module", str(outside_dir))
    assert result is None


def test_nested_package_structure(crawler, tmp_path):
    """Modules in nested package structures are found."""
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()

    subpkg_dir = pkg_dir / "subpkg"
    subpkg_dir.mkdir()

    module_file = subpkg_dir / "module.py"
    module_file.touch()

    result = crawler.find_local_module("pkg.subpkg.module", str(tmp_path))
    assert result == str(module_file)


def test_prefer_file_over_package(crawler, tmp_path):
    """Single 'modulename.py' files are preferred over packages with the same name."""
    module_file = tmp_path / "module.py"
    module_file.touch()

    module_dir = tmp_path / "module"
    module_dir.mkdir()

    init_file = module_dir / "__init__.py"
    init_file.touch()

    result = crawler.find_local_module("module", str(tmp_path))
    assert result == str(module_file)


def test_empty_module_name(crawler, tmp_path):
    """Empty module names return None."""
    result = crawler.find_local_module("", str(tmp_path))
    assert result is None
