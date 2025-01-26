import ast
from typing import Dict, List
from depgraph.parse_file import parse_file



def analyze_file(file_path: str, depth: int) -> Dict[str, List[ast.AST]]:
    """
    Analyze a Python file by parsing it into an AST and finding variable assignments.

    Args:
        file_path: Path to the Python file to analyze
        depth: Maximum depth to traverse the AST (not implemented yet)

    Returns:
        A dictionary mapping scopes to lists of assignment nodes
    """
    ast_tree: ast.Module = parse_file(file_path)
    return {
        "tbd": [ast_tree],
    }
