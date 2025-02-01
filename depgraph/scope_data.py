from dataclasses import dataclass
from typing import Dict, Optional, Union, Literal, get_args
import ast


@dataclass(frozen=True)
class ScopeName:
    """Represents a fully qualified scope name in Python code.

    A scope name is a dot-separated path representing the nesting of scopes,
    starting from the module scope. For example:
    - "<module>"
    - "<module>.MyClass"
    - "<module>.outer.Inner.method"
    - "<module>.function.<lambda_line_1>"

    Attributes:
        value: The full scope name string
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the scope name format."""
        if not self.value:
            raise ValueError("Scope name cannot be empty")

        # Allow "<module>" and names that start with "<module>."
        # Any other validation is handled by ScopeInfo
        if self.value != "<module>" and "." in self.value and not self.value.startswith("<module>."):
            raise ValueError("Hierarchical scope names must start with '<module>'")

    @property
    def is_module(self) -> bool:
        """Whether this is the module scope."""
        return self.value == "<module>"

    @property
    def parent(self) -> Optional["ScopeName"]:
        """Get the parent scope name, if any."""
        if self.is_module:
            return None

        last_dot = self.value.rfind(".")
        if last_dot == -1:
            return None

        parent_str = self.value[:last_dot]
        if parent_str == "<module":  # Handle the case of direct module children
            parent_str = "<module>"
        return ScopeName(parent_str)

    @property
    def local_name(self) -> str:
        """Get the local name of this scope (without parent path)."""
        return self.value.rsplit(".", 1)[-1]

    def child(self, name: str) -> "ScopeName":
        """Create a child scope name under this scope.

        Args:
            name: The local name of the child scope

        Returns:
            A new ScopeName representing the child scope
        """
        return ScopeName(f"{self.value}.{name}")

    def __str__(self) -> str:
        return self.value

    def __bool__(self) -> bool:
        """Return True if the scope name is not empty."""
        return bool(self.value)


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
        name: The fully qualified name of the scope (e.g. "<module>.class.function")
        node: The AST node that defines this scope
        type: The type of scope (module, class, function, etc.)
        parent: The name of the parent scope, if any
    """

    name: ScopeName
    node: ScopeNode
    type: ScopeType
    parent: Optional[ScopeName] = None

    def __post_init__(self) -> None:
        """Validate scope information after initialization."""
        valid_types = get_args(ScopeType)
        if self.type not in valid_types:
            raise TypeError(
                f"Invalid scope type: {self.type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )

        node_type_mapping = {
            "module": ast.Module,
            "class": ast.ClassDef,
            "function": ast.FunctionDef,
            "async_function": ast.AsyncFunctionDef,
            "lambda": ast.Lambda,
            "listcomp": ast.ListComp,
            "setcomp": ast.SetComp,
            "dictcomp": ast.DictComp,
            "genexpr": ast.GeneratorExp,
            "match": ast.Match,
        }

        expected_type = node_type_mapping.get(self.type)
        if expected_type and not isinstance(self.node, expected_type):
            raise TypeError(
                f"Invalid node type for scope type '{self.type}'. "
                f"Expected {expected_type.__name__}, got {type(self.node).__name__}"
            )

        if not self.name:
            raise ValueError("Scope name cannot be empty")

        if self.type == "module" and not self.name.is_module:
            raise ValueError("Module scope must be named '<module>'")

        if self.type != "module" and not self.parent:
            raise ValueError(f"Non-module scope '{self.name}' must have a parent scope")


@dataclass
class FileAnalysis:
    """Contains the analysis results for a Python source file.

    Attributes:
        file_path: The path to the analyzed file
        scopes: Dictionary mapping scope names to their ScopeInfo
        ast_tree: AST of the analyzed file
    """

    file_path: str
    scopes: Dict[ScopeName, ScopeInfo]
    ast_tree: ast.Module

    def get_scope_by_filter(self, scope_filter: str) -> Optional[ScopeInfo]:
        """Get a specific scope by its fully qualified name.

        Args:
            scope_filter: The fully qualified scope name (e.g. "<module>.outer.Inner.method")

        Returns:
            The ScopeInfo for the requested scope if found, None otherwise
        """
        return self.scopes.get(ScopeName(scope_filter))
