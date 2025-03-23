import ast
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch
from depgraph.import_crawler.process_imports import process_imports
from depgraph.import_crawler.file_dependency_graph import FileDependencyGraph


def test_process_basic_import():
    """Process basic 'import module' statements."""
    code = "import os"
    tree = ast.parse(code)
    file_path = Path("test.py")
    module_dir = Path("/test")
    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    with patch('depgraph.import_crawler.process_imports.resolve_import') as mock_resolve:
        process_imports(tree, file_path, module_dir, graph, stdlib_paths, visited_paths)
        
        mock_resolve.assert_called_once_with(
            module_name_str="os",
            current_file_path=file_path,
            search_dir=module_dir,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )


def test_process_multiple_imports():
    """Process multiple imports in a single import statement."""
    code = "import os, sys, typing"
    tree = ast.parse(code)
    file_path = Path("test.py")
    module_dir = Path("/test")
    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    with patch('depgraph.import_crawler.process_imports.resolve_import') as mock_resolve:
        process_imports(tree, file_path, module_dir, graph, stdlib_paths, visited_paths)
        
        assert mock_resolve.call_count == 3
        expected_calls = [
            ((
                "module_name_str", "os",
                "current_file_path", file_path,
                "search_dir", module_dir,
                "graph", graph,
                "stdlib_paths", stdlib_paths,
                "visited_paths", visited_paths,
            ),),
            ((
                "module_name_str", "sys",
                "current_file_path", file_path,
                "search_dir", module_dir,
                "graph", graph,
                "stdlib_paths", stdlib_paths,
                "visited_paths", visited_paths,
            ),),
            ((
                "module_name_str", "typing",
                "current_file_path", file_path,
                "search_dir", module_dir,
                "graph", graph,
                "stdlib_paths", stdlib_paths,
                "visited_paths", visited_paths,
            ),),
        ]
        # Check that each expected call is in the actual calls
        for expected in expected_calls:
            found = False
            for actual in mock_resolve.call_args_list:
                if all(expected[0][i] == actual[1][expected[0][i-1]] for i in range(1, len(expected[0]), 2)):
                    found = True
                    break
            assert found, f"Expected call {expected} not found"


def test_process_from_import():
    """Process 'from module import name' statements."""
    code = "from os import path"
    tree = ast.parse(code)
    file_path = Path("test.py")
    module_dir = Path("/test")
    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    with patch('depgraph.import_crawler.process_imports.resolve_import') as mock_resolve:
        process_imports(tree, file_path, module_dir, graph, stdlib_paths, visited_paths)
        
        mock_resolve.assert_called_once_with(
            module_name_str="os",
            current_file_path=file_path,
            search_dir=module_dir,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )


def test_process_from_import_multiple():
    """Process 'from module import name1, name2' statements."""
    code = "from os import path, getcwd"
    tree = ast.parse(code)
    file_path = Path("test.py")
    module_dir = Path("/test")
    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    with patch('depgraph.import_crawler.process_imports.resolve_import') as mock_resolve:
        process_imports(tree, file_path, module_dir, graph, stdlib_paths, visited_paths)
        
        mock_resolve.assert_called_once_with(
            module_name_str="os",
            current_file_path=file_path,
            search_dir=module_dir,
            graph=graph,
            stdlib_paths=stdlib_paths,
            visited_paths=visited_paths,
        )


def test_process_nested_imports():
    """Process imports within functions or classes."""
    code = dedent("""
        import os
        def func():
            import sys
        class MyClass:
            import typing
    """)

    tree = ast.parse(code)
    file_path = Path("test.py")
    module_dir = Path("/test")
    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    with patch('depgraph.import_crawler.process_imports.resolve_import') as mock_resolve:
        process_imports(tree, file_path, module_dir, graph, stdlib_paths, visited_paths)
        
        assert mock_resolve.call_count == 3
        expected_calls = [
            ((
                "module_name_str", "os",
                "current_file_path", file_path,
                "search_dir", module_dir,
                "graph", graph,
                "stdlib_paths", stdlib_paths,
                "visited_paths", visited_paths,
            ),),
            ((
                "module_name_str", "sys",
                "current_file_path", file_path,
                "search_dir", module_dir,
                "graph", graph,
                "stdlib_paths", stdlib_paths,
                "visited_paths", visited_paths,
            ),),
            ((
                "module_name_str", "typing",
                "current_file_path", file_path,
                "search_dir", module_dir,
                "graph", graph,
                "stdlib_paths", stdlib_paths,
                "visited_paths", visited_paths,
            ),),
        ]
        # Check that each expected call is in the actual calls
        for expected in expected_calls:
            found = False
            for actual in mock_resolve.call_args_list:
                if all(expected[0][i] == actual[1][expected[0][i-1]] for i in range(1, len(expected[0]), 2)):
                    found = True
                    break
            assert found, f"Expected call {expected} not found"


def test_process_empty_from_import():
    """Process 'from . import name' statements"""
    code = "from . import module"
    tree = ast.parse(code)
    file_path = Path("test.py")
    module_dir = Path("/test")
    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    with patch('depgraph.import_crawler.process_imports.resolve_import') as mock_resolve:
        process_imports(tree, file_path, module_dir, graph, stdlib_paths, visited_paths)
        
        # Should NOT resolve_import for relative imports with no module name
        assert mock_resolve.call_count == 0


def test_process_complex_imports():
    """Process a mix of different import types."""
    code = dedent("""
        import os
        from sys import path
        from typing import List, Optional
        import datetime, time
        from pathlib import Path
    """)

    tree = ast.parse(code)
    file_path = Path("test.py")
    module_dir = Path("/test")
    graph = FileDependencyGraph()
    visited_paths = set()
    stdlib_paths = set()

    with patch('depgraph.import_crawler.process_imports.resolve_import') as mock_resolve:
        process_imports(tree, file_path, module_dir, graph, stdlib_paths, visited_paths)
        
        assert mock_resolve.call_count == 6
        
        expected_modules = ["os", "sys", "typing", "datetime", "time", "pathlib"]
        
        # Check that each module was resolved
        for module in expected_modules:
            found = False
            for call in mock_resolve.call_args_list:
                if call[1]["module_name_str"] == module:
                    found = True
                    break
            assert found, f"Expected module {module} not found in resolve_import calls"
