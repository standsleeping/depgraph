import sys
from unittest.mock import patch


def test_find_local_module_in_syspath(crawler, tmp_path):
    """Local modules in the path are found."""
    module_dir = tmp_path / "package"
    module_dir.mkdir()

    module_file = module_dir / "test_module.py"
    module_file.touch()

    with patch.object(sys, "path", [str(module_dir)] + sys.path):
        result = crawler.find_module_in_syspath("test_module")
        assert result == module_file


def test_nonexistent_module(crawler):
    """Nonexistent modules return None."""
    result = crawler.find_module_in_syspath("nonexistent_module")
    assert result is None


def test_stdlib_module(crawler):
    """Standard library modules return None."""
    result = crawler.find_module_in_syspath("os")
    assert result is None


def test_compiled_module(crawler, tmp_path):
    """Compiled modules return None."""
    compiled_spec = type(
        "ModuleSpec",
        (),
        {
            "origin": str(tmp_path / "module.so"),
        },
    )

    find_spec_patch = "depgraph.import_crawler.import_crawler.find_spec"
    with patch(find_spec_patch, return_value=compiled_spec):
        result = crawler.find_module_in_syspath("compiled_module")
        assert result is None


def test_non_local_module(crawler, tmp_path):
    """Non-local modules return None."""
    outside_dir = tmp_path.parent / "outside"
    outside_dir.mkdir(exist_ok=True)

    outside_module = outside_dir / "outside_module.py"
    outside_module.touch()

    with patch.object(sys, "path", [str(outside_dir)] + sys.path):
        result = crawler.find_module_in_syspath("outside_module")
        assert result is None


def test_import_error_handling(crawler):
    """ImportErrors during module lookup result in None."""
    find_spec_patch = "depgraph.import_crawler.import_crawler.find_spec"
    with patch(find_spec_patch, side_effect=ImportError):
        result = crawler.find_module_in_syspath("problematic_module")
        assert result is None


def test_attribute_error_handling(crawler):
    """AttributeErrors during module lookup result in None."""
    find_spec_patch = "depgraph.import_crawler.import_crawler.find_spec"
    with patch(find_spec_patch, side_effect=AttributeError):
        result = crawler.find_module_in_syspath("problematic_module")
        assert result is None


def test_none_spec_handling(crawler):
    """When specs are not found, return None."""
    find_spec_patch = "depgraph.import_crawler.import_crawler.find_spec"
    with patch(find_spec_patch, return_value=None):
        result = crawler.find_module_in_syspath("nonexistent_module")
        assert result is None


def test_spec_without_origin(crawler):
    """When specs have no origin attribute, return None."""
    spec_without_origin = type("ModuleSpec", (), {})

    find_spec_patch = "depgraph.import_crawler.import_crawler.find_spec"
    with patch(find_spec_patch, return_value=spec_without_origin):
        result = crawler.find_module_in_syspath("module_without_origin")
        assert result is None
