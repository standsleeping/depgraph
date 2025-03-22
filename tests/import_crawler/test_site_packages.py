import pytest
from pathlib import Path
from depgraph.import_crawler.site_packages import find_project_site_packages
from depgraph.logger.setup_logger import setup_logger


@pytest.fixture
def logger():
    return setup_logger()


def test_finds_venv_site_packages(tmp_path, logger):
    """Finds site-packages in a virtual environment."""
    # Create venv structure
    venv_dir = tmp_path / "venv"
    site_packages = venv_dir / "lib" / "python3.8" / "site-packages"
    site_packages.mkdir(parents=True)

    result = find_project_site_packages(tmp_path, logger)
    assert site_packages.resolve() in result


def test_finds_dot_venv_site_packages(tmp_path, logger):
    """Finds site-packages in a .venv directory."""
    venv_dir = tmp_path / ".venv"
    site_packages = venv_dir / "lib" / "python3.8" / "site-packages"
    site_packages.mkdir(parents=True)

    result = find_project_site_packages(tmp_path, logger)
    assert site_packages.resolve() in result


def test_stops_at_project_marker_pyproject(tmp_path, logger):
    """Stops searching at pyproject.toml marker."""
    # Create nested structure
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (tmp_path / "pyproject.toml").touch()

    # Create venv in parent (should not be found)
    parent_venv = tmp_path.parent / "venv"
    parent_site_packages = parent_venv / "lib" / "python3.8" / "site-packages"
    parent_site_packages.mkdir(parents=True)

    result = find_project_site_packages(subdir, logger)
    assert parent_site_packages.resolve() not in result


def test_stops_at_project_marker_requirements(tmp_path, logger):
    """Stops searching at requirements.txt marker."""
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (tmp_path / "requirements.txt").touch()

    result = find_project_site_packages(subdir, logger)
    assert len(result) > 0  # Should fall back to system site-packages


def test_fallback_to_system_site_packages(tmp_path, logger):
    """Falls back to system site-packages when no venv found."""
    result = find_project_site_packages(tmp_path, logger)

    # Should find at least one system site-packages directory
    assert len(result) > 0
    assert all("site-packages" in str(p) for p in result)


def test_multiple_python_versions_in_venv(tmp_path, logger):
    """Finds site-packages for multiple Python versions in venv."""
    venv_dir = tmp_path / "venv" / "lib"
    venv_dir.mkdir(parents=True)

    # Create multiple Python version directories
    py38 = venv_dir / "python3.8" / "site-packages"
    py39 = venv_dir / "python3.9" / "site-packages"
    py38.mkdir(parents=True)
    py39.mkdir(parents=True)

    result = find_project_site_packages(tmp_path, logger)
    assert py38.resolve() in result
    assert py39.resolve() in result


def test_finds_venv_in_project_root(tmp_path, logger):
    """Correctly identifies site-packages in project root virtual environment."""
    # Create a mock project structure
    project_root = tmp_path / "myproject"
    project_root.mkdir()

    # Create a virtual environment
    venv_dir = project_root / "venv"
    site_packages = venv_dir / "lib" / "python3.8" / "site-packages"
    site_packages.mkdir(parents=True)

    # Create a marker file to indicate project root
    (project_root / "pyproject.toml").touch()

    result = find_project_site_packages(project_root, logger)
    assert site_packages.resolve() in result