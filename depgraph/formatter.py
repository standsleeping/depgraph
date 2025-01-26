import ast
from typing import Dict, List


def print_analysis(analysis: Dict[str, List[ast.AST]]) -> None:
    """Print the analysis.

    Args:
        analysis: The analysis to print
    """
    print(analysis)
