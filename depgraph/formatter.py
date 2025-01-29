from typing import Dict, Optional
from .scope_data import ScopeInfo, FileAnalysis


def print_analysis(analysis: FileAnalysis, scope_filter: Optional[str] = None) -> None:
    """Print the analysis in a hierarchical tree format.

    Args:
        analysis: The analysis to print
        scope_filter: Optional fully qualified scope name to filter the output
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
    if scope_filter:
        if scope_filter not in analysis.scopes:
            print(f"Error: Scope '{scope_filter}' not found")
            return
        print_scope(scope_filter, analysis.scopes)
    else:
        print_scope("<module>", analysis.scopes)
