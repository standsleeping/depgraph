from typing import List
from depgraph.visitors.data.scope_info import ScopeInfo
from depgraph.visitors.data.assignment_data import AssignmentData
from depgraph.visitors.assignment_visitor import AssignmentVisitor


def process_scope(scope: ScopeInfo) -> List[AssignmentData]:
    """Process all assignments within the given scope.

    Args:
        scope: A scope to analyze

    Returns:
        A list of AssignmentData objects representing all assignments in the scope
    """
    visitor = AssignmentVisitor(scope.name)
    visitor.visit(scope.node)
    return visitor.assignments
