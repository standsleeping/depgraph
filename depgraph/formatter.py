from typing import Dict
from .scope_data import ScopeInfo, FileAnalysis


def print_analysis(analysis: FileAnalysis) -> None:
    """Print the analysis in a hierarchical tree format.

    Args:
        analysis: The analysis to print
    """

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
    print_scope("<module>", analysis.scopes)
