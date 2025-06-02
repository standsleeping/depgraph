from depgraph.cli.functions.analyze_file import analyze_file


def test_analyze_file_with_process_file():
    """Analyzes process_file.py and returns structured results."""
    target_file = "./src/depgraph/processors/process_file.py"

    result = analyze_file(file_path=target_file, depth=3, scope_filter=None)

    # Verify structure of returned dict
    assert isinstance(result, dict)
    assert "graph" in result
    assert "unresolved_imports" in result
    assert isinstance(result["graph"], dict)
    assert isinstance(result["unresolved_imports"], dict)

    # Verify graph has expected structure (it's a dict of files with their dependencies)
    graph = result["graph"]
    assert isinstance(graph, dict)

    # Verify we have some files in the graph (the file should have dependencies)
    assert len(graph) > 0

    # Verify each file entry has expected structure
    for filename, file_info in graph.items():
        assert isinstance(file_info, dict)
        assert "imported_by" in file_info
        assert "imports" in file_info
        assert isinstance(file_info["imported_by"], list)
        assert isinstance(file_info["imports"], list)
