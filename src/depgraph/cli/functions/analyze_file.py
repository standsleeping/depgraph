from pathlib import Path
from typing import Dict, Any
from depgraph.processors import analyze_file as processor_analyze_file
from depgraph.formatters.process_output import process_output


def analyze_file(
    file_path: str | Path, depth: int = 4, scope_filter: str | None = None
) -> Dict[str, Any]:
    """Analyze a Python file and return structured analysis results.

    Args:
        file_path: Path to the Python file to analyze
        depth: Depth of the analysis
        scope_filter: Optional scope name to filter the output

    Returns:
        Dictionary containing analysis results with keys:
        - file_analysis data
        - assignments
        - graph (dependency graph)
        - unresolved_imports
    """
    # Get raw analysis results from processors
    raw_results = processor_analyze_file(
        file_path=file_path, depth=depth, scope_filter=scope_filter
    )

    # Format the results using formatters
    formatted_output = process_output(
        analysis=raw_results["file_analysis"],
        scope_filter=raw_results["scope_filter"],
        assignments=raw_results["assignments"],
    )

    # Add graph and unresolved imports to formatted output
    formatted_output["graph"] = raw_results["graph"]
    formatted_output["unresolved_imports"] = raw_results["unresolved_imports"]

    return formatted_output
