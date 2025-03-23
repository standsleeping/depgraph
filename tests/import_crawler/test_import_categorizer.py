import os
import pytest
from unittest.mock import Mock, patch
from depgraph.import_crawler.import_categorizer import ImportCategorizer


@pytest.fixture
def stdlib_paths():
    return {"/usr/lib/python3.8", "/usr/local/lib/python3.8"}


@pytest.fixture
def site_packages_paths(tmp_path):
    site_pkg = tmp_path / "site-packages"
    site_pkg.mkdir()
    return {site_pkg}



@pytest.fixture
def categorizer(stdlib_paths, site_packages_paths):
    return ImportCategorizer(stdlib_paths, site_packages_paths)


def test_categorize_builtin_module(categorizer):
    """Categorizes built-in modules."""
    with patch(
        "depgraph.import_crawler.import_categorizer.find_spec"
    ) as mock_find_spec:
        mock_find_spec.return_value = Mock(origin="built-in")

        categorizer.categorize_import("sys")

        assert "sys" in categorizer.system_imports
        assert "sys" not in categorizer.third_party_imports
        assert "sys" not in categorizer.local_imports


def test_categorize_stdlib_module(categorizer, stdlib_paths):
    """Categorizes standard library modules."""
    stdlib_module = os.path.join(list(stdlib_paths)[0], "os.py")

    with patch(
        "depgraph.import_crawler.import_categorizer.find_spec"
    ) as mock_find_spec:
        mock_find_spec.return_value = Mock(origin=stdlib_module)

        categorizer.categorize_import("os")

        assert "os" in categorizer.system_imports
        assert "os" not in categorizer.third_party_imports
        assert "os" not in categorizer.local_imports


def test_categorize_third_party_module(categorizer, site_packages_paths):
    """Categorizes third-party modules."""
    site_pkg = list(site_packages_paths)[0]
    third_party_module = str(site_pkg / "requests.py")

    with patch(
        "depgraph.import_crawler.import_categorizer.find_spec"
    ) as mock_find_spec:
        mock_find_spec.return_value = Mock(origin=third_party_module)

        categorizer.categorize_import("requests")

        assert "requests" in categorizer.third_party_imports
        assert "requests" not in categorizer.system_imports
        assert "requests" not in categorizer.local_imports


def test_categorize_local_module(categorizer):
    """Categorizes local modules when spec lookup fails."""
    with patch(
        "depgraph.import_crawler.import_categorizer.find_spec"
    ) as mock_find_spec:
        mock_find_spec.return_value = None

        categorizer.categorize_import("local_module")

        assert "local_module" in categorizer.local_imports
        assert "local_module" not in categorizer.system_imports
        assert "local_module" not in categorizer.third_party_imports


def test_categorize_third_party_package_directory(categorizer, site_packages_paths):
    """Categorizes third-party packages that exist as directories."""
    site_pkg = list(site_packages_paths)[0]
    package_dir = site_pkg / "django"
    package_dir.mkdir()

    with patch(
        "depgraph.import_crawler.import_categorizer.find_spec"
    ) as mock_find_spec:
        mock_find_spec.return_value = None

        categorizer.categorize_import("django")

        assert "django" in categorizer.third_party_imports
        assert "django" not in categorizer.system_imports
        assert "django" not in categorizer.local_imports


def test_categorize_import_error_handling(categorizer):
    """Handles ImportError during spec lookup gracefully."""
    with patch(
        "depgraph.import_crawler.import_categorizer.find_spec"
    ) as mock_find_spec:
        mock_find_spec.side_effect = ImportError

        categorizer.categorize_import("problematic_module")

        assert "problematic_module" in categorizer.local_imports


def test_categorize_attribute_error_handling(categorizer):
    """Handles AttributeError during spec lookup gracefully."""
    with patch(
        "depgraph.import_crawler.import_categorizer.find_spec"
    ) as mock_find_spec:
        mock_find_spec.side_effect = AttributeError

        categorizer.categorize_import("problematic_module")

        assert "problematic_module" in categorizer.local_imports
