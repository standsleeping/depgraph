from unittest.mock import patch

from depgraph.import_crawler.module_info import ModuleInfo


def test_resolve_local_import(crawler, tmp_path):
    """Successfully resolves and adds local module to graph."""
    local_module = tmp_path / "local_module.py"
    local_module.touch()

    current_file = tmp_path / "current.py"
    current_file.touch()

    crawler.resolve_import("local_module", current_file, tmp_path)

    key = ModuleInfo(current_file)
    value = ModuleInfo(local_module)

    assert crawler.graph[key] == {value}


def test_resolve_nonexistent_module(crawler, tmp_path):
    """Handles nonexistent modules gracefully."""
    current_file = tmp_path / "current.py"
    current_file.touch()

    # Does not raise any exceptions
    crawler.resolve_import("nonexistent", current_file, tmp_path)

    # Graph does not contain the current file (no import was resolved)
    assert current_file not in crawler.graph


def test_resolve_multiple_imports(crawler, tmp_path):
    """Successfully adds multiple imports to the graph."""
    module1 = tmp_path / "module1.py"
    module1.touch()
    module2 = tmp_path / "module2.py"
    module2.touch()
    current_file = tmp_path / "current.py"
    current_file.touch()

    crawler.resolve_import("module1", current_file, tmp_path)
    crawler.resolve_import("module2", current_file, tmp_path)

    key = ModuleInfo(current_file)
    value1 = ModuleInfo(module1)
    value2 = ModuleInfo(module2)

    assert crawler.graph[key] == {value1, value2}


def test_resolve_recursive_imports(crawler, tmp_path):
    """Handles recursive imports through build_graph."""
    # Chain of imports: current -> module1 -> module2
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"
    current_file = tmp_path / "current.py"

    module2.touch()
    module1.write_text("import module2")
    current_file.touch()

    # Mock build_graph to track calls
    with patch.object(crawler, "build_graph") as mock_build:
        crawler.resolve_import("module1", current_file, tmp_path)

        # Should call build_graph on module1
        mock_build.assert_called_once_with(module1)


def test_resolve_duplicate_imports(crawler, tmp_path):
    """Handles duplicate imports gracefully."""
    local_module = tmp_path / "local_module.py"
    local_module.touch()

    current_file = tmp_path / "current.py"
    current_file.touch()

    # Resolve import twice
    crawler.resolve_import("local_module", current_file, tmp_path)
    crawler.resolve_import("local_module", current_file, tmp_path)

    # Only appears once in the graph
    key = ModuleInfo(current_file)
    value = ModuleInfo(local_module)
    assert crawler.graph[key] == {value}


def test_resolve_import_updates_existing_set(crawler, tmp_path):
    """Correctly updates existing import sets in the graph."""
    module1 = tmp_path / "module1.py"
    module1.touch()

    module2 = tmp_path / "module2.py"
    module2.touch()

    current_file = tmp_path / "current.py"
    current_file.touch()

    # Manually add existing import
    key = ModuleInfo(current_file)
    value1 = ModuleInfo(module1)
    crawler.graph[key] = {value1}

    # Resolve another import
    crawler.resolve_import("module2", current_file, tmp_path)

    # Preserves existing import and add new one
    key = ModuleInfo(current_file)
    value1 = ModuleInfo(module1)
    value2 = ModuleInfo(module2)
    assert crawler.graph[key] == {value1, value2}


def test_resolve_import_circular_reference(crawler, tmp_path):
    """Handles circular imports correctly."""
    # Create files with circular imports
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"

    module1.write_text("import module2")
    module2.write_text("import module1")

    # Mock build_graph to prevent infinite recursion
    with patch.object(crawler, "build_graph") as mock_build:
        crawler.resolve_import("module1", module2, tmp_path)

        # Should only call build_graph once for module1
        mock_build.assert_called_once_with(module1)


def test_categorize_unresolved_imports(crawler, tmp_path):
    """Correctly categorizes different types of unresolved imports."""
    current_file = tmp_path / "test.py"
    current_file.touch()

    # System import
    crawler.resolve_import("sys", current_file, tmp_path)
    assert "sys" in crawler.unresolved_system_imports

    # Default to local import
    crawler.resolve_import("local_module", current_file, tmp_path)
    assert "local_module" in crawler.unresolved_local_imports


def test_categorize_dotted_imports(crawler, tmp_path):
    """Correctly categorizes dotted imports as local."""
    current_file = tmp_path / "test.py"
    current_file.touch()

    # Test dotted imports (should be local)
    crawler.resolve_import("package.module", current_file, tmp_path)
    assert "package.module" in crawler.unresolved_local_imports


def test_categorize_private_imports(crawler, tmp_path):
    """Correctly categorizes private imports as local."""
    current_file = tmp_path / "test.py"
    current_file.touch()

    # Test private module import (should be local)
    crawler.resolve_import("_private_module", current_file, tmp_path)
    assert "_private_module" in crawler.unresolved_local_imports
