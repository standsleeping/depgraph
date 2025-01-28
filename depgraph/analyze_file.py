import ast
from depgraph.parse_file import parse_file
from depgraph.scope_visitor import ScopeVisitor
from depgraph.scope_data import FileAnalysis


def analyze_file(file_path: str, depth: int) -> FileAnalysis:
    """
    Analyze a Python file by parsing it into an AST and identifying scopes.

    Args:
        file_path: Path to the Python file to analyze
        depth: Maximum depth to traverse the AST (not implemented yet)

    Returns:
        FileAnalysis object containing the complete analysis results,
        including all scopes and their relationships
    """
    ast_tree: ast.Module = parse_file(file_path)
    visitor = ScopeVisitor()
    visitor.visit(ast_tree)
    return FileAnalysis(file_path=file_path, scopes=visitor.scopes, ast_tree=ast_tree)
