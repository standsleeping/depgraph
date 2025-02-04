import os
import pytest


def test_local_module_in_project_root(crawler, tmp_path):
    """Modules in the project root are considered local."""
    local_module = tmp_path / "local_module.py"
    local_module.touch()

    assert crawler.is_local_module(str(local_module)) is True


def test_local_module_in_subdirectory(crawler, tmp_path):
    """Modules in project subdirectories are considered local."""
    subdir = tmp_path / "subpackage"
    subdir.mkdir()
    local_module = subdir / "local_module.py"
    local_module.touch()

    assert crawler.is_local_module(str(local_module)) is True


def test_module_outside_project_root(crawler, tmp_path):
    """Modules outside the project root are not considered local."""
    outside_dir = tmp_path.parent / "outside"
    outside_dir.mkdir(exist_ok=True)

    outside_module = outside_dir / "outside_module.py"
    outside_module.touch()

    assert crawler.is_local_module(str(outside_module)) is False


def test_stdlib_module(crawler):
    """Standard library modules are not considered local."""
    # Grab a standard library path from the crawler's stdlib_paths
    stdlib_path = next(iter(crawler.stdlib_paths))
    test_module = os.path.join(stdlib_path, "test_module.py")

    assert crawler.is_local_module(test_module) is False


def test_nonexistent_module(crawler, tmp_path):
    """Modules that don't exist are not considered local."""
    nonexistent = tmp_path / "nonexistent.py"
    assert crawler.is_local_module(str(nonexistent)) is True


def test_relative_path_resolution(crawler, tmp_path):
    """Relative paths are properly resolved."""
    local_module = tmp_path / "local_module.py"
    local_module.touch()

    relative_path = "./local_module.py"
    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(tmp_path)
        assert crawler.is_local_module(relative_path) is True
