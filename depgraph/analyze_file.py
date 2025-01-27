import ast
from typing import Dict
from depgraph.parse_file import parse_file
from depgraph.scope_visitor import ScopeVisitor


def analyze_file(file_path: str, depth: int) -> Dict[str, ast.AST]:
    """
    Analyze a Python file by parsing it into an AST and finding all scopes.

    Args:
        file_path: Path to the Python file to analyze
        depth: Maximum depth to traverse the AST (not implemented yet)

    Returns:
        A dictionary mapping scope names to their AST nodes
    """
    ast_tree: ast.Module = parse_file(file_path)
    visitor = ScopeVisitor()
    visitor.visit(ast_tree)
    return visitor.scopes
