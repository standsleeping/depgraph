from dataclasses import dataclass
from typing import Dict, Optional, Union, Literal
import ast

ScopeNode = Union[
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Lambda,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.Match,
]

ScopeType = Literal[
    "module",
    "class",
    "function",
    "async_function",
    "lambda",
    "listcomp",
    "setcomp",
    "dictcomp",
    "genexpr",
    "match",
]


@dataclass
class ScopeInfo:
    """Information about a scope in Python code.

    A scope is a region of code where names (variables, functions, etc.) are valid.
    This could be a module, class, function, or comprehension scope.

    Attributes:
        name: The fully qualified name of the scope (e.g. "module.class.function")
        node: The AST node that defines this scope
        type: The type of scope (module, class, function, etc.)
        parent: The name of the parent scope, if any
    """

    name: str
    node: ScopeNode
    type: ScopeType
    parent: Optional[str] = None


@dataclass
class FileAnalysis:
    """Contains the analysis results for a Python source file.

    Attributes:
        file_path: The path to the analyzed file
        scopes: Dictionary mapping scope names to their ScopeInfo
        ast_tree: AST of the analyzed file
    """

    file_path: str
    scopes: Dict[str, ScopeInfo]
    ast_tree: ast.Module

    def get_scope_by_filter(self, scope_filter: str) -> Optional[ScopeInfo]:
        """Get a specific scope by its fully qualified name.

        Args:
            scope_filter: The fully qualified scope name (e.g. "<module>.outer.Inner.method")

        Returns:
            The ScopeInfo for the requested scope if found, None otherwise
        """
        return self.scopes.get(scope_filter)
