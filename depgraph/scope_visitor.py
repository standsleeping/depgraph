import ast
from typing import Dict, Optional
from depgraph.scope_data import ScopeInfo


class ScopeVisitor(ast.NodeVisitor):
    """AST visitor that identifies scopes in Python code.

    For each scope-defining node, it:
    1. Creates a qualified name based on the current scope path
    2. Creates a ScopeInfo object to track the scope's properties
    3. Maintains the current scope context while visiting child nodes

    Example of scope tree for:
        def outer():
            class Inner:
                def method(): pass

    This would create scopes:
        "<module>"
        "<module>.outer"
        "<module>.outer.Inner"
        "<module>.outer.Inner.method"

    Each scope tracks:
    - Qualified name
    - The AST node that defined it
    - Type (module, class, function, etc)
    - Parent scope
    """

    def __init__(self) -> None:
        super().__init__()
        self.scopes: Dict[str, ScopeInfo] = {}
        self.current_scope: Optional[str] = None

    def _make_scope_name(self, name: str) -> str:
        """Creates a qualified scope name based on the current scope.

        Args:
            name: The local name of the scope

        Returns:
            Fully qualified scope name including parent scope path
        """
        return f"{self.current_scope}.{name}" if self.current_scope else name

    def _add_scope(self, node: ast.AST, name: str, scope_type: str) -> None:
        """Add a new scope to the visitor's scope dictionary.

        Args:
            node: The AST node that defines the scope
            name: The name of the scope
            scope_type: The type of scope (module, class, function, etc.)
        """
        scope_info = ScopeInfo(
            name=name, node=node, type=scope_type, parent=self.current_scope
        )

        self.scopes[name] = scope_info

    def visit_Module(self, node: ast.Module) -> None:
        """Visit a module node, creating the root scope."""
        self._add_scope(node, "<module>", "module")
        prev_scope = self.current_scope
        self.current_scope = "<module>"
        self.generic_visit(node)
        self.current_scope = prev_scope

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition, creating a new class scope."""
        scope_name = self._make_scope_name(node.name)
        self._add_scope(node, scope_name, "class")
        prev_scope = self.current_scope
        self.current_scope = scope_name
        self.generic_visit(node)
        self.current_scope = prev_scope

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition, creating a new function scope."""
        scope_name = self._make_scope_name(node.name)
        self._add_scope(node, scope_name, "function")
        prev_scope = self.current_scope
        self.current_scope = scope_name
        self.generic_visit(node)
        self.current_scope = prev_scope

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition, creating a new function scope."""
        scope_name = self._make_scope_name(node.name)
        self._add_scope(node, scope_name, "async_function")
        prev_scope = self.current_scope
        self.current_scope = scope_name
        self.generic_visit(node)
        self.current_scope = prev_scope

    def visit_Lambda(self, node: ast.Lambda) -> None:
        """Visit a lambda expression, creating a new function scope."""
        scope_name = self._make_scope_name(f"<lambda_line_{node.lineno}>")
        self._add_scope(node, scope_name, "lambda")
        prev_scope = self.current_scope
        self.current_scope = scope_name
        self.generic_visit(node)
        self.current_scope = prev_scope
