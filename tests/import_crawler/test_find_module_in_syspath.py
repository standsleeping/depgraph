import sys
from pathlib import Path
from unittest.mock import patch
from depgraph.import_crawler.find_module_in_syspath import find_module_in_syspath


def test_find_local_module_in_syspath(tmp_path):
    """Local modules in the path are found."""
    module_dir = tmp_path / "package"
    module_dir.mkdir()

    module_file = module_dir / "test_module.py"
    module_file.touch()

    with patch.object(sys, "path", [str(module_dir)] + sys.path):
        result = find_module_in_syspath(
            module_name="test_module",
            parent_path=tmp_path,
            stdlib_paths=set(),
        )
        assert result == module_file


def test_nonexistent_module(tmp_path):
    """Nonexistent modules return None."""
    result = find_module_in_syspath(
        module_name="nonexistent_module",
        parent_path=tmp_path,
        stdlib_paths=set(),
    )
    assert result is None


def test_stdlib_module(tmp_path):
    """Standard library modules return None."""
    # Create a mock stdlib_paths set with a path that contains the os module
    stdlib_path = Path(sys.modules["os"].__file__).parent
    stdlib_paths = {stdlib_path}
    
    result = find_module_in_syspath(
        module_name="os",
        parent_path=tmp_path,
        stdlib_paths=stdlib_paths,
    )
    assert result is None


def test_compiled_module(tmp_path):
    """Compiled modules return None."""
    compiled_spec = type(
        "ModuleSpec",
        (),
        {
            "origin": str(tmp_path / "module.so"),
        },
    )

    find_spec_patch = "depgraph.import_crawler.find_module_in_syspath.find_spec"
    with patch(find_spec_patch, return_value=compiled_spec):
        result = find_module_in_syspath(
            module_name="compiled_module",
            parent_path=tmp_path,
            stdlib_paths=set(),
        )
        assert result is None


def test_non_local_module(tmp_path):
    """Non-local modules return None."""
    outside_dir = tmp_path.parent / "outside"
    outside_dir.mkdir(exist_ok=True)

    outside_module = outside_dir / "outside_module.py"
    outside_module.touch()

    with patch.object(sys, "path", [str(outside_dir)] + sys.path):
        result = find_module_in_syspath(
            module_name="outside_module",
            parent_path=tmp_path,
            stdlib_paths=set(),
        )
        assert result is None


def test_import_error_handling(tmp_path):
    """ImportErrors during module lookup result in None."""
    find_spec_patch = "depgraph.import_crawler.find_module_in_syspath.find_spec"
    with patch(find_spec_patch, side_effect=ImportError):
        result = find_module_in_syspath(
            module_name="problematic_module",
            parent_path=tmp_path,
            stdlib_paths=set(),
        )
        assert result is None


def test_attribute_error_handling(tmp_path):
    """AttributeErrors during module lookup result in None."""
    find_spec_patch = "depgraph.import_crawler.find_module_in_syspath.find_spec"
    with patch(find_spec_patch, side_effect=AttributeError):
        result = find_module_in_syspath(
            module_name="problematic_module",
            parent_path=tmp_path,
            stdlib_paths=set(),
        )
        assert result is None


def test_none_spec_handling(tmp_path):
    """When specs are not found, return None."""
    find_spec_patch = "depgraph.import_crawler.find_module_in_syspath.find_spec"
    with patch(find_spec_patch, return_value=None):
        result = find_module_in_syspath(
            module_name="nonexistent_module",
            parent_path=tmp_path,
            stdlib_paths=set(),
        )
        assert result is None


def test_spec_without_origin(tmp_path):
    """When specs have no origin attribute, return None."""
    spec_without_origin = type("ModuleSpec", (), {})

    find_spec_patch = "depgraph.import_crawler.find_module_in_syspath.find_spec"
    with patch(find_spec_patch, return_value=spec_without_origin):
        result = find_module_in_syspath(
            module_name="module_without_origin",
            parent_path=tmp_path,
            stdlib_paths=set(),
        )
        assert result is None
