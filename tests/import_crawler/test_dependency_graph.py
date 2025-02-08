from pathlib import Path
from depgraph.import_crawler.module_info import ModuleInfo
from depgraph.import_crawler.dependency_graph import DependencyGraph


def test_add_dependency():
    """Adds dependencies to the graph."""
    graph = DependencyGraph()

    # Create test modules
    mod_a = ModuleInfo(Path("/path/to/a.py"))
    mod_b = ModuleInfo(Path("/path/to/b.py"))

    # Add dependency
    graph.add_dependency(mod_a, mod_b)

    # Verify dependency was added
    assert mod_b in graph.dependencies[mod_a]
    assert mod_b in graph.dependencies
    assert len(graph.dependencies[mod_b]) == 0


def test_to_json_simple():
    """Converts a simple graph to JSON format."""
    graph = DependencyGraph()

    # Create test modules
    mod_a = ModuleInfo(Path("/path/to/a.py"))
    mod_b = ModuleInfo(Path("/path/to/b.py"))

    # Add dependencies
    graph.add_dependency(mod_a, mod_b)

    # Convert to JSON
    json_graph = graph.to_json()

    # Verify JSON structure
    assert str(mod_a) in json_graph
    assert str(mod_b) in json_graph
    assert json_graph[str(mod_a)]["imports"] == [str(mod_b)]
    assert json_graph[str(mod_a)]["imported_by"] == []
    assert json_graph[str(mod_b)]["imports"] == []
    assert json_graph[str(mod_b)]["imported_by"] == [str(mod_a)]


def test_to_json_complex():
    """Converts a more complex graph to JSON format."""
    graph = DependencyGraph()

    # Create test modules
    mod_a = ModuleInfo(Path("/path/to/a.py"))
    mod_b = ModuleInfo(Path("/path/to/b.py"))
    mod_c = ModuleInfo(Path("/path/to/c.py"))

    # Add dependencies
    graph.add_dependency(mod_a, mod_b)
    graph.add_dependency(mod_b, mod_c)
    graph.add_dependency(mod_a, mod_c)

    # Convert to JSON
    json_graph = graph.to_json()

    # Verify JSON structure
    assert json_graph[str(mod_a)]["imports"] == sorted([str(mod_b), str(mod_c)])
    assert json_graph[str(mod_b)]["imports"] == [str(mod_c)]
    assert json_graph[str(mod_c)]["imports"] == []

    assert json_graph[str(mod_a)]["imported_by"] == []
    assert json_graph[str(mod_b)]["imported_by"] == [str(mod_a)]
    assert sorted(json_graph[str(mod_c)]["imported_by"]) == sorted(
        [str(mod_a), str(mod_b)]
    )


def test_to_json_empty():
    """Converts an empty graph to JSON format."""
    graph = DependencyGraph()
    json_graph = graph.to_json()
    assert json_graph == {}


def test_add_dependency_idempotent():
    """Adds the same dependency multiple times works correctly."""
    graph = DependencyGraph()

    mod_a = ModuleInfo(Path("/path/to/a.py"))
    mod_b = ModuleInfo(Path("/path/to/b.py"))

    # Add same dependency multiple times
    graph.add_dependency(mod_a, mod_b)
    graph.add_dependency(mod_a, mod_b)

    # Verify dependency was added only once
    assert len(graph.dependencies[mod_a]) == 1
    assert mod_b in graph.dependencies[mod_a]
