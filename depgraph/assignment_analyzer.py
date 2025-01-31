from dataclasses import dataclass
from typing import List, Literal, Union, get_args
import ast
from .scope_data import ScopeInfo


AssignmentType = Literal["basic", "augmented", "annotated"]

AssignmentNode = Union[
    ast.Assign,  # Basic assignment (x = 1)
    ast.AugAssign,  # Augmented assignment (x += 1)
    ast.AnnAssign,  # Annotated assignment (x: int = 1)
]


@dataclass
class AssignmentData:
    """Represents a variable assignment in Python code.

    Attributes:
        name: The name of the variable being assigned
        node: The AST node representing the assignment (Assign, AugAssign, or AnnAssign)
        type: The type of assignment (basic, augmented, annotated, etc.)
    """

    name: str
    node: AssignmentNode
    type: AssignmentType

    def __post_init__(self) -> None:
        """Validate the assignment type after initialization."""
        valid_types = get_args(AssignmentType)
        if self.type not in valid_types:
            raise TypeError(
                f"Invalid assignment type: {self.type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )


class AssignmentVisitor(ast.NodeVisitor):
    """AST visitor that collects variable assignments within a scope."""

    def __init__(self) -> None:
        self.assignments: List[AssignmentData] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        """Basic assignments like 'x = 1'."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignments.append(
                    AssignmentData(name=target.id, node=node, type="basic")
                )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Augmented assignments like 'x += 1'."""
        if isinstance(node.target, ast.Name):
            self.assignments.append(
                AssignmentData(name=node.target.id, node=node, type="augmented")
            )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Annotated assignments like 'x: int = 1'."""
        if isinstance(target := node.target, ast.Name):
            self.assignments.append(
                AssignmentData(name=target.id, node=node, type="annotated")
            )
        self.generic_visit(node)


class ScopeAssignmentAnalyzer:
    """Analyzes variable assignments within a specific scope."""

    def analyze_scope(self, scope: ScopeInfo) -> List[AssignmentData]:
        """Analyze all assignments within the given scope.

        Args:
            scope: A scope to analyze

        Returns:
            A list of AssignmentData objects representing all assignments in the scope
        """
        visitor = AssignmentVisitor()
        visitor.visit(scope.node)
        return visitor.assignments
