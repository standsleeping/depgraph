from unittest.mock import patch
from depgraph.import_crawler.file_info import FileInfo
from depgraph.import_crawler.file_dependency_graph import FileDependencyGraph
from depgraph.import_crawler.resolve_import import resolve_import
from depgraph.import_crawler.import_categorizer import ImportCategorizer


def test_resolve_local_import(tmp_path):
    """Successfully resolves and adds local module to graph."""
    local_module = tmp_path / "local_module.py"
    local_module.touch()

    current_file = tmp_path / "current.py"
    current_file.touch()

    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    visited_paths = set()
    stdlib_paths = set()

    resolve_import(
        module_name_str="local_module",
        current_file_path=current_file,
        search_dir=tmp_path,
        graph=graph,
        stdlib_paths=stdlib_paths,
        visited_paths=visited_paths,
    )

    key = FileInfo(current_file)
    value = FileInfo(local_module)

    assert graph[key] == {value}


def test_resolve_nonexistent_module(tmp_path):
    """Handles nonexistent modules gracefully."""
    current_file = tmp_path / "current.py"
    current_file.touch()

    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    visited_paths = set()
    stdlib_paths = set()

    # Does not raise any exceptions
    resolve_import(
        module_name_str="nonexistent",
        current_file_path=current_file,
        search_dir=tmp_path,
        graph=graph,
        stdlib_paths=stdlib_paths,
        visited_paths=visited_paths,
    )

    # Graph does not contain the current file (no import was resolved)
    current_str = str(current_file)
    assert not any(str(k.full_path) == current_str for k in graph.dependencies)


def test_resolve_multiple_imports(tmp_path):
    """Successfully adds multiple imports to the graph."""
    module1 = tmp_path / "module1.py"
    module1.touch()
    module2 = tmp_path / "module2.py"
    module2.touch()
    current_file = tmp_path / "current.py"
    current_file.touch()

    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    visited_paths = set()
    stdlib_paths = set()

    resolve_import(
        module_name_str="module1",
        current_file_path=current_file,
        search_dir=tmp_path,
        graph=graph,
        stdlib_paths=stdlib_paths,
        visited_paths=visited_paths,
    )
    
    resolve_import(
        module_name_str="module2",
        current_file_path=current_file,
        search_dir=tmp_path,
        graph=graph,
        stdlib_paths=stdlib_paths,
        visited_paths=visited_paths,
    )

    key = FileInfo(current_file)
    value1 = FileInfo(module1)
    value2 = FileInfo(module2)

    assert graph[key] == {value1, value2}


def test_resolve_recursive_imports(tmp_path):
    """Handles recursive imports through build_graph."""
    # Chain of imports: current -> module1 -> module2
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"
    current_file = tmp_path / "current.py"

    module2.touch()
    module1.write_text("import module2")
    current_file.touch()

    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    visited_paths = set()
    stdlib_paths = set()

    # Since build_graph is imported inside the function, 
    # we need to patch at the module where it is defined
    with patch('depgraph.import_crawler.build_graph.build_graph') as mock_build:
        resolve_import(
            module_name_str="module1",
            current_file_path=current_file,
            search_dir=tmp_path,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )

        # Should call build_graph on module1
        mock_build.assert_called_once()
        # Check the file_path parameter
        assert mock_build.call_args[1]["file_path"] == module1


def test_resolve_duplicate_imports(tmp_path):
    """Handles duplicate imports gracefully."""
    local_module = tmp_path / "local_module.py"
    local_module.touch()

    current_file = tmp_path / "current.py"
    current_file.touch()

    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    visited_paths = set()
    stdlib_paths = set()

    # Resolve import twice
    resolve_import(
        module_name_str="local_module",
        current_file_path=current_file,
        search_dir=tmp_path,
        graph=graph,
        stdlib_paths=stdlib_paths,
        visited_paths=visited_paths,
    )
    
    resolve_import(
        module_name_str="local_module",
        current_file_path=current_file,
        search_dir=tmp_path,
        graph=graph,
        stdlib_paths=stdlib_paths,
        visited_paths=visited_paths,
    )

    # Only appears once in the graph
    key = FileInfo(current_file)
    value = FileInfo(local_module)
    assert graph[key] == {value}


def test_resolve_import_updates_existing_set(tmp_path):
    """Correctly updates existing import sets in the graph."""
    module1 = tmp_path / "module1.py"
    module1.touch()

    module2 = tmp_path / "module2.py"
    module2.touch()

    current_file = tmp_path / "current.py"
    current_file.touch()

    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    visited_paths = set()
    stdlib_paths = set()

    # Manually add existing import
    key = FileInfo(current_file)
    value1 = FileInfo(module1)
    graph[key] = {value1}

    # Resolve another import
    resolve_import(
        module_name_str="module2",
        current_file_path=current_file,
        search_dir=tmp_path,
        graph=graph,
        stdlib_paths=stdlib_paths,
        visited_paths=visited_paths,
    )

    # Preserves existing import and add new one
    key = FileInfo(current_file)
    value1 = FileInfo(module1)
    value2 = FileInfo(module2)
    assert graph[key] == {value1, value2}


def test_resolve_import_circular_reference(tmp_path):
    """Handles circular imports correctly."""
    # Create files with circular imports
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"

    module1.write_text("import module2")
    module2.write_text("import module1")

    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    visited_paths = set()
    stdlib_paths = set()

    # Mock build_graph to prevent infinite recursion
    with patch('depgraph.import_crawler.build_graph.build_graph') as mock_build:
        resolve_import(
            module_name_str="module1",
            current_file_path=module2,
            search_dir=tmp_path,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )

        # Should only call build_graph once for module1
        mock_build.assert_called_once()
        # Check the file_path parameter
        assert mock_build.call_args[1]["file_path"] == module1


def test_categorize_unresolved_imports(tmp_path):
    """Correctly categorizes different types of unresolved imports."""
    current_file = tmp_path / "test.py"
    current_file.touch()

    # Create a graph with a mock ImportCategorizer
    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    stdlib_paths = set()
    visited_paths = set()

    # Mock find_module to return None so we test the categorization
    with patch('depgraph.import_crawler.resolve_import.find_module', return_value=None):
        # System import
        resolve_import(
            module_name_str="sys",
            current_file_path=current_file,
            search_dir=tmp_path,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )
        assert "sys" in graph.import_categorizer.system_imports

        # Default to local import
        resolve_import(
            module_name_str="local_module",
            current_file_path=current_file,
            search_dir=tmp_path,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )
        assert "local_module" in graph.import_categorizer.local_imports


def test_categorize_dotted_imports(tmp_path):
    """Correctly categorizes dotted imports as local."""
    current_file = tmp_path / "test.py"
    current_file.touch()

    # Create a graph with a mock ImportCategorizer
    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    stdlib_paths = set()
    visited_paths = set()

    # Mock find_module to return None so we test the categorization
    with patch('depgraph.import_crawler.resolve_import.find_module', return_value=None):
        # Test dotted imports (should be local)
        resolve_import(
            module_name_str="package.module",
            current_file_path=current_file,
            search_dir=tmp_path,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )
        assert "package.module" in graph.import_categorizer.local_imports


def test_categorize_private_imports(tmp_path):
    """Correctly categorizes private imports as local."""
    current_file = tmp_path / "test.py"
    current_file.touch()

    # Create a graph with a mock ImportCategorizer
    graph = FileDependencyGraph()
    graph.import_categorizer = ImportCategorizer(set(), set())
    stdlib_paths = set()
    visited_paths = set()

    # Mock find_module to return None so we test the categorization
    with patch('depgraph.import_crawler.resolve_import.find_module', return_value=None):
        # Test private module import (should be local)
        resolve_import(
            module_name_str="_private_module",
            current_file_path=current_file,
            search_dir=tmp_path,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )
        assert "_private_module" in graph.import_categorizer.local_imports
