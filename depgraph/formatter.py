from typing import Dict, Optional, List
from .scope_data import ScopeInfo, FileAnalysis, ScopeName
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
            "annotated": ": type =",
        }
        return f"{assignment.name} ({type_indicators[assignment.type]})"

    def print_scope(
        scope_name: ScopeName, scopes: Dict[ScopeName, ScopeInfo], indent: int = 0
    ) -> None:
        scope_info = scopes[scope_name]
        prefix = "  " * indent
        print(f"{prefix}└─ {scope_name} ({scope_info.type})")

        children = [
            name for name, info in scopes.items() if str(info.parent) == str(scope_name)
        ]
        for child in sorted(children, key=lambda x: str(x)):
            print_scope(child, scopes, indent + 1)

    print("\nScope Hierarchy:")
    if scope_filter:
        if scope_filter not in [str(name) for name in analysis.scopes.keys()]:
            print(f"Error: Scope '{scope_filter}' not found")
            return
        print_scope(ScopeName(scope_filter), analysis.scopes)
    else:
        print_scope(ScopeName("<module>"), analysis.scopes)

    if assignments:
        print("\nAssignments:")
        for assignment in sorted(assignments, key=lambda x: x.name):
            print(f"  • {format_assignment(assignment)}")
