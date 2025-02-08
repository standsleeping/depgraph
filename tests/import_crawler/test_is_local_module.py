import os
import pytest
from depgraph.import_crawler.is_local_module import is_local_module


@pytest.fixture
def stdlib_paths():
    """Returns a list of standard library paths."""
    return ["/usr/lib/python3.8", "/usr/local/lib/python3.8"]


@pytest.fixture
def project_root(tmp_path):
    """Returns a temporary project root directory."""
    return str(tmp_path)


def test_local_module_in_project_root(stdlib_paths, project_root):
    """Modules in the project root are considered local."""
    local_module = os.path.join(project_root, "local_module.py")

    result = is_local_module(
        local_module,
        stdlib_paths,
        project_root,
    )

    assert result is True


def test_local_module_in_subdirectory(stdlib_paths, project_root):
    """Modules in project subdirectories are considered local."""
    subdir = os.path.join(project_root, "subpackage")
    os.makedirs(subdir)
    local_module = os.path.join(subdir, "local_module.py")

    result = is_local_module(
        local_module,
        stdlib_paths,
        project_root,
    )

    assert result is True


def test_module_outside_project_root(stdlib_paths, project_root):
    """Modules outside the project root are not considered local."""
    outside_dir = os.path.dirname(project_root)
    outside_module = os.path.join(outside_dir, "outside_module.py")

    result = is_local_module(
        outside_module,
        stdlib_paths,
        project_root,
    )

    assert result is False


def test_stdlib_module(stdlib_paths, project_root):
    """Standard library modules are not considered local."""
    stdlib_module = os.path.join(stdlib_paths[0], "test_module.py")

    result = is_local_module(
        stdlib_module,
        stdlib_paths,
        project_root,
    )

    assert result is False


def test_relative_path_resolution(stdlib_paths, project_root):
    """Relative paths are properly resolved."""
    relative_path = "./local_module.py"

    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(project_root)

        result = is_local_module(
            relative_path,
            stdlib_paths,
            project_root,
        )

        assert result is True
