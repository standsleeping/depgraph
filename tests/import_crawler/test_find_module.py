import pytest
import os


def test_find_local_module_first(crawler, tmp_path):
    """Local modules are found before checking sys.path."""
    local_module = tmp_path / "test_module.py"
    local_module.touch()

    result = crawler.find_module("test_module", str(tmp_path))
    assert result == str(local_module)


def test_fallback_to_syspath(crawler, tmp_path):
    """Falls back to sys.path when local module not found."""
    other_dir = tmp_path / "other"
    other_dir.mkdir()

    module_file = other_dir / "test_module.py"
    module_file.touch()

    with pytest.MonkeyPatch.context() as mp:
        mp.syspath_prepend(str(other_dir))
        result = crawler.find_module("test_module", str(tmp_path))
        assert result == str(module_file)


def test_nonexistent_module(crawler, tmp_path):
    """Returns None when module is not found anywhere."""
    result = crawler.find_module("nonexistent_module", str(tmp_path))
    assert result is None


def test_package_module(crawler, tmp_path):
    """Finds modules within packages."""
    package_dir = tmp_path / "mypackage"
    package_dir.mkdir()

    init_file = package_dir / "__init__.py"
    init_file.touch()

    submodule = package_dir / "submodule.py"
    submodule.touch()

    result = crawler.find_module("mypackage.submodule", str(tmp_path))
    assert result == str(submodule)


def test_non_local_module(crawler, tmp_path):
    """Returns None for non-local modules."""
    outside_dir = tmp_path.parent / "outside"
    outside_dir.mkdir(exist_ok=True)

    outside_module = outside_dir / "outside_module.py"
    outside_module.touch()

    result = crawler.find_module("outside_module", str(outside_dir))
    assert result is None


def test_relative_path_resolution(crawler, tmp_path):
    """Resolves relative paths correctly."""
    module_dir = tmp_path / "package"
    module_dir.mkdir()

    module_file = module_dir / "test_module.py"
    module_file.touch()

    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(tmp_path)
        result = crawler.find_module("package.test_module", "./")
        assert os.path.abspath(result) == str(module_file)
