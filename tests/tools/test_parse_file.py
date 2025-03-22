import ast
import pytest
from pathlib import Path

from depgraph.tools import parse_file


def test_parses_file(tmp_path):
    """
    Parses a file and returns an AST.
    """

    test_file = tmp_path / "test.py"
    test_file.write_text("x = 1\ny = 2\n")
    tree = parse_file(test_file)

    assert isinstance(tree, ast.Module)
    assert len(tree.body) == 2
    assert all(isinstance(node, ast.Assign) for node in tree.body)


def test_raises_file_not_found():
    """
    Raises a FileNotFoundError when the file does not exist.
    """
    with pytest.raises(FileNotFoundError):
        parse_file(Path("nonexistent.py"))


def test_raises_syntax_error(tmp_path):
    """
    Raises a SyntaxError when the file contains invalid Python syntax.
    """
    test_file = tmp_path / "invalid.py"
    test_file.write_text("this is not valid python")

    with pytest.raises(SyntaxError):
        parse_file(test_file)