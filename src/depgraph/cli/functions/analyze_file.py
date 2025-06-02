from pathlib import Path
from typing import Dict, Any
from depgraph.processors import process_file
from depgraph.processors.data.file_analysis import FileAnalysis
from depgraph.visitors.data.scope_info import ScopeInfo
from depgraph.visitors.data.scope_name import ScopeName
from depgraph.processors.process_scope import process_scope
from depgraph.import_crawler.crawl import crawl
from depgraph.formatters.process_output import process_output
from depgraph.tools.convert_to_abs_path import convert_to_abs_path


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
    abs_file_path: Path = convert_to_abs_path(str(file_path))

    file_analysis: FileAnalysis = process_file(abs_file_path=abs_file_path, depth=depth)

    module_scope_info: ScopeInfo
    if scope_filter:
        module_scope_info = file_analysis.scopes[ScopeName(scope_filter)]
    else:
        module_scope_info = file_analysis.scopes[ScopeName("<module>")]

    assignments = process_scope(module_scope_info)

    output: Dict[str, Any] = process_output(
        analysis=file_analysis,
        scope_filter=scope_filter,
        assignments=assignments,
    )

    graph, unresolved_imports = crawl(
        abs_file_path=abs_file_path,
    )

    json_graph = graph.to_json()

    output["graph"] = json_graph
    output["unresolved_imports"] = unresolved_imports

    return output
