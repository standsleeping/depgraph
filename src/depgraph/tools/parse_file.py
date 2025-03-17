import ast
from pathlib import Path


def parse_file(file_path: str) -> ast.Module:
    """
    Parse a Python file into an AST.

    Args:
        file_path: Path to the Python file to parse

    Returns:
        The AST of the parsed file
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=str(path))
        return tree
    except SyntaxError as e:
        raise SyntaxError(f"Failed to parse {file_path}: {str(e)}")
