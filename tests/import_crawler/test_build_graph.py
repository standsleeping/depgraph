from textwrap import dedent

from depgraph.import_crawler.module_info import ModuleInfo


def test_build_graph_single_file(crawler, tmp_path):
    """Builds graph for a single file with no imports."""
    test_file = tmp_path / "test.py"
    test_file.write_text("x = 1\ny = 2\n")

    crawler.build_graph(str(test_file))
    assert str(test_file) in crawler.visited
    assert str(test_file) not in crawler.graph


def test_build_graph_with_imports(crawler, tmp_path):
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

    crawler.build_graph(str(main_file))

    assert str(main_file) in crawler.visited
    key = ModuleInfo(str(main_file))
    value1 = ModuleInfo(str(module1))
    value2 = ModuleInfo(str(module2))
    assert crawler.graph[key] == {value1, value2}


def test_build_graph_nested_imports(crawler, tmp_path):
    """Builds graph with nested import dependencies."""
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"
    module3 = tmp_path / "module3.py"
    main_file = tmp_path / "main.py"

    module1.write_text("import module2")
    module2.write_text("import module3")
    module3.write_text("x = 3")
    main_file.write_text("import module1")

    crawler.build_graph(str(main_file))

    assert str(main_file) in crawler.visited
    assert str(module1) in crawler.visited
    assert str(module2) in crawler.visited
    assert str(module3) in crawler.visited

    key = ModuleInfo(str(main_file))
    value1 = ModuleInfo(str(module1))
    assert crawler.graph[key] == {value1}

    key = ModuleInfo(str(module1))
    value2 = ModuleInfo(str(module2))
    assert crawler.graph[key] == {value2}

    key = ModuleInfo(str(module2))
    value3 = ModuleInfo(str(module3))
    assert crawler.graph[key] == {value3}


def test_build_graph_circular_imports(crawler, tmp_path):
    """Handles circular import dependencies."""
    module1 = tmp_path / "module1.py"
    module2 = tmp_path / "module2.py"

    module1.write_text("import module2")
    module2.write_text("import module1")

    crawler.build_graph(str(module1))

    assert str(module1) in crawler.visited
    assert str(module2) in crawler.visited

    key = ModuleInfo(str(module1))
    value2 = ModuleInfo(str(module2))
    assert crawler.graph[key] == {value2}

    key = ModuleInfo(str(module2))
    value1 = ModuleInfo(str(module1))
    assert crawler.graph[key] == {value1}


def test_build_graph_package_imports(crawler, tmp_path):
    """Builds graph with package imports."""
    pkg_dir = tmp_path / "mypackage"
    pkg_dir.mkdir()

    init_file = pkg_dir / "__init__.py"
    init_file.write_text("from . import submodule")

    submodule = pkg_dir / "submodule.py"
    submodule.write_text("x = 1")

    main_file = tmp_path / "main.py"
    main_file.write_text("import mypackage")

    crawler.build_graph(str(main_file))

    assert str(main_file) in crawler.visited
    assert str(init_file) in crawler.visited
    key = ModuleInfo(str(main_file))
    value = ModuleInfo(str(init_file))
    assert crawler.graph[key] == {value}


def test_build_graph_nonexistent_import(crawler, tmp_path):
    """Handles nonexistent imports gracefully."""
    main_file = tmp_path / "main.py"
    main_file.write_text("import nonexistent_module")

    crawler.build_graph(str(main_file))

    assert str(main_file) in crawler.visited
    assert str(main_file) not in crawler.graph


def test_build_graph_syntax_error(crawler, tmp_path):
    """Handles files with syntax errors gracefully."""
    main_file = tmp_path / "main.py"
    main_file.write_text("Not valid python!")

    crawler.build_graph(str(main_file))

    assert str(main_file) in crawler.visited
    assert str(main_file) not in crawler.graph


def test_build_graph_already_visited(crawler, tmp_path):
    """Skips already visited files."""
    test_file = tmp_path / "test.py"
    test_file.write_text("x = 1")

    crawler.visited.add(str(test_file))

    crawler.build_graph(str(test_file))
    assert str(test_file) not in crawler.graph


def test_build_graph_non_py_file(crawler, tmp_path):
    """Skips non-Python files."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("not a python file")

    crawler.build_graph(str(test_file))

    assert str(test_file) not in crawler.visited
    assert str(test_file) not in crawler.graph
