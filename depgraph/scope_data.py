from dataclasses import dataclass
from typing import Dict, Optional
import ast

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
    node: ast.AST
    type: str
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