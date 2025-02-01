from typing import Dict, Optional, List
from .scope_data import ScopeInfo, FileAnalysis
from .assignment_analyzer import AssignmentData


def print_analysis(
    *,
    analysis: FileAnalysis,
    scope_filter: Optional[str] = None,
    assignments: List[AssignmentData],
) -> None:
    """Print the analysis in a hierarchical tree format.

    Args:
        analysis: The analysis to print
        scope_filter: Optional fully qualified scope name to filter the output
        assignments: List of assignments found in the analyzed file
    """

    def format_assignment(assignment: AssignmentData) -> str:
        """Format a single assignment for display."""
        type_indicators = {
            "basic": "=",
            "augmented": "+=/-=/*=/etc",
            "annotated": ": type ="
        }
        return f"{assignment.name} ({type_indicators[assignment.type]})"

    def print_scope(
        scope_name: str, scopes: Dict[str, ScopeInfo], indent: int = 0
    ) -> None:
        scope_info = scopes[scope_name]
        prefix = "  " * indent
        print(f"{prefix}└─ {scope_name} ({scope_info.type})")

        children = [name for name, info in scopes.items() if info.parent == scope_name]
        for child in sorted(children):
            print_scope(child, scopes, indent + 1)

    print("\nScope Hierarchy:")
    if scope_filter:
        if scope_filter not in analysis.scopes:
            print(f"Error: Scope '{scope_filter}' not found")
            return
        print_scope(scope_filter, analysis.scopes)
    else:
        print_scope("<module>", analysis.scopes)

    if assignments:
        print("\nAssignments:")
        for assignment in sorted(assignments, key=lambda x: x.name):
            print(f"  • {format_assignment(assignment)}")
