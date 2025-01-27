import ast
from typing import Dict, List


class ScopeVisitor(ast.NodeVisitor):
    """Visits AST nodes and builds an index of all scopes in the code."""

    def __init__(self) -> None:
        self.scopes: Dict[str, ast.AST] = {}
        self.current_scope: List[str] = []

    def _make_scope_name(self) -> str:
        """Creates a dot-separated scope name from the current scope stack."""
        return ".".join(self.current_scope) if self.current_scope else "<module>"

    def visit_Module(self, node: ast.Module) -> None:
        """Visit the module (top-level) scope."""
        self.scopes["<module>"] = node
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to track function scopes."""
        self.current_scope.append(node.name)
        scope_name = self._make_scope_name()
        self.scopes[scope_name] = node
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to track class scopes."""
        self.current_scope.append(node.name)
        scope_name = self._make_scope_name()
        self.scopes[scope_name] = node
        self.generic_visit(node)
        self.current_scope.pop()
