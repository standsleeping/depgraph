import ast
from textwrap import dedent
from unittest.mock import Mock


def test_process_basic_import(crawler):
    """Process basic 'import module' statements."""
    code = "import os"
    tree = ast.parse(code)

    # Mocking resolve_import to track calls
    crawler.resolve_import = Mock()

    crawler.process_imports(tree, "test.py", "/test")
    crawler.resolve_import.assert_called_once_with("os", "test.py", "/test")


def test_process_multiple_imports(crawler):
    """Process multiple imports in a single import statement."""
    code = "import os, sys, typing"
    tree = ast.parse(code)

    crawler.resolve_import = Mock()

    crawler.process_imports(tree, "test.py", "/test")

    assert crawler.resolve_import.call_count == 3
    crawler.resolve_import.assert_any_call("os", "test.py", "/test")
    crawler.resolve_import.assert_any_call("sys", "test.py", "/test")
    crawler.resolve_import.assert_any_call("typing", "test.py", "/test")


def test_process_from_import(crawler):
    """Process 'from module import name' statements."""
    code = "from os import path"
    tree = ast.parse(code)

    crawler.resolve_import = Mock()

    crawler.process_imports(tree, "test.py", "/test")

    crawler.resolve_import.assert_called_once_with("os", "test.py", "/test")


def test_process_from_import_multiple(crawler):
    """Process 'from module import name1, name2' statements."""
    code = "from os import path, getcwd"
    tree = ast.parse(code)

    crawler.resolve_import = Mock()

    crawler.process_imports(tree, "test.py", "/test")

    crawler.resolve_import.assert_called_once_with("os", "test.py", "/test")


def test_process_nested_imports(crawler):
    """Process imports within functions or classes."""
    code = dedent("""
        import os
        def func():
            import sys
        class MyClass:
            import typing
    """)

    tree = ast.parse(code)

    crawler.resolve_import = Mock()

    crawler.process_imports(tree, "test.py", "/test")

    assert crawler.resolve_import.call_count == 3
    crawler.resolve_import.assert_any_call("os", "test.py", "/test")
    crawler.resolve_import.assert_any_call("sys", "test.py", "/test")
    crawler.resolve_import.assert_any_call("typing", "test.py", "/test")


def test_process_empty_from_import(crawler):
    """Process 'from . import name' statements"""
    code = "from . import module"
    tree = ast.parse(code)

    crawler.resolve_import = Mock()

    crawler.process_imports(tree, "test.py", "/test")
    # Should NOT resolve_import for relative imports with no module name
    assert crawler.resolve_import.call_count == 0


def test_process_complex_imports(crawler):
    """Process a mix of different import types."""
    code = dedent("""
        import os
        from sys import path
        from typing import List, Optional
        import datetime, time
        from pathlib import Path
    """)

    tree = ast.parse(code)

    crawler.resolve_import = Mock()

    crawler.process_imports(tree, "test.py", "/test")

    assert crawler.resolve_import.call_count == 6
    crawler.resolve_import.assert_any_call("os", "test.py", "/test")
    crawler.resolve_import.assert_any_call("sys", "test.py", "/test")
    crawler.resolve_import.assert_any_call("typing", "test.py", "/test")
    crawler.resolve_import.assert_any_call("datetime", "test.py", "/test")
    crawler.resolve_import.assert_any_call("time", "test.py", "/test")
    crawler.resolve_import.assert_any_call("pathlib", "test.py", "/test")
