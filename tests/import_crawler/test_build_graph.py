from textwrap import dedent
from depgraph.import_crawler.file_info import FileInfo
from depgraph.import_crawler.file_dependency_graph import FileDependencyGraph
from depgraph.import_crawler.build_graph import build_graph


def test_build_graph_single_file(tmp_path):
    """Builds graph for a single file with no imports."""
    test_file = tmp_path / "test.py"
    test_file.write_text("x = 1\ny = 2\n")

    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    result = build_graph(
        file_path=test_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    assert test_file in visited_paths
    assert len(result.dependencies) == 0


def test_build_graph_with_imports(tmp_path):
    """Builds graph for a file with imports."""
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"
    main_file = tmp_path / "main.py"

    module1.write_text("x = 1")
    module2.write_text("y = 2")

    content = dedent("""
        import module1
        import module2
    """)

    main_file.write_text(content)

    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    result = build_graph(
        file_path=main_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    assert main_file in visited_paths

    key = FileInfo(main_file)
    value1 = FileInfo(module1)
    value2 = FileInfo(module2)
    assert result[key] == {value1, value2}


def test_build_graph_nested_imports(tmp_path):
    """Builds graph with nested import dependencies."""
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"
    module3 = tmp_path / "module3.py"
    main_file = tmp_path / "main.py"

    module1.write_text("import module2")
    module2.write_text("import module3")
    module3.write_text("x = 3")
    main_file.write_text("import module1")

    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    result = build_graph(
        file_path=main_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    assert main_file in visited_paths
    assert module1 in visited_paths
    assert module2 in visited_paths
    assert module3 in visited_paths

    key = FileInfo(main_file)
    value1 = FileInfo(module1)
    assert result[key] == {value1}

    key = FileInfo(module1)
    value2 = FileInfo(module2)
    assert result[key] == {value2}

    key = FileInfo(module2)
    value3 = FileInfo(module3)
    assert result[key] == {value3}


def test_build_graph_circular_imports(tmp_path):
    """Handles circular import dependencies."""
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"

    module1.write_text("import module2")
    module2.write_text("import module1")

    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    result = build_graph(
        file_path=module1,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    assert module1 in visited_paths
    assert module2 in visited_paths

    key = FileInfo(module1)
    value2 = FileInfo(module2)
    assert result[key] == {value2}

    key = FileInfo(module2)
    value1 = FileInfo(module1)
    assert result[key] == {value1}


def test_build_graph_package_imports(tmp_path):
    """Builds graph with package imports."""
    pkg_dir = tmp_path / "mypackage"
    pkg_dir.mkdir()

    init_file = pkg_dir / "__init__.py"
    init_file.write_text("from . import submodule")

    submodule = pkg_dir / "submodule.py"
    submodule.write_text("x = 1")

    main_file = tmp_path / "main.py"
    main_file.write_text("import mypackage")

    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    result = build_graph(
        file_path=main_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    assert main_file in visited_paths
    assert init_file in visited_paths

    key = FileInfo(main_file)
    value = FileInfo(init_file)
    assert result[key] == {value}


def test_build_graph_syntax_error(tmp_path):
    """Handles files with syntax errors gracefully."""
    main_file = tmp_path / "main.py"
    main_file.write_text("Not valid python!")

    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    result = build_graph(
        file_path=main_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    assert main_file in visited_paths
    assert len(result.dependencies) == 0


def test_build_graph_already_visited(tmp_path):
    """Skips already visited files."""
    test_file = tmp_path / "test.py"
    test_file.write_text("x = 1")

    graph = FileDependencyGraph()
    visited_paths = {test_file}  # Already visited
    stdlib_paths = set()

    result = build_graph(
        file_path=test_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    assert len(result.dependencies) == 0


def test_build_graph_non_py_file(tmp_path):
    """Skips non-Python files."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("not a python file")

    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    result = build_graph(
        file_path=test_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    assert test_file not in visited_paths
    assert len(result.dependencies) == 0
