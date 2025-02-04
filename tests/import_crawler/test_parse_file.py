import ast
from textwrap import dedent


def test_parse_valid_file(crawler, tmp_path):
    """Successfully parses a valid Python file."""
    test_file = tmp_path / "test.py"
    test_file.write_text("x = 1\ny = 2\n")

    result = crawler.parse_file(str(test_file))

    assert isinstance(result, ast.Module)
    assert len(result.body) == 2
    assert all(isinstance(node, ast.Assign) for node in result.body)


def test_parse_empty_file(crawler, tmp_path):
    """Successfully parses an empty Python file."""
    test_file = tmp_path / "empty.py"
    test_file.write_text("")

    result = crawler.parse_file(str(test_file))

    assert isinstance(result, ast.Module)
    assert len(result.body) == 0


def test_parse_nonexistent_file(crawler):
    """Returns None for nonexistent files."""
    result = crawler.parse_file("nonexistent.py")
    assert result is None


def test_parse_invalid_syntax(crawler, tmp_path):
    """Returns None for files with invalid Python syntax."""
    test_file = tmp_path / "invalid.py"
    test_file.write_text("Not valid python!")

    result = crawler.parse_file(str(test_file))
    assert result is None


def test_parse_with_imports(crawler, tmp_path):
    """Successfully parses files with import statements."""
    content = dedent("""
        import os
        from sys import path
        from typing import Optional, List
    """).strip()

    test_file = tmp_path / "imports.py"
    test_file.write_text(content)

    result = crawler.parse_file(str(test_file))

    assert isinstance(result, ast.Module)
    assert len(result.body) == 3
    assert isinstance(result.body[0], ast.Import)
    assert isinstance(result.body[1], ast.ImportFrom)
    assert isinstance(result.body[2], ast.ImportFrom)
