from depgraph.cli.data.analysis_config import AnalysisConfig
from depgraph.tools.convert_to_abs_path import convert_to_abs_path


def prepare_analysis_config(
    file_path: str, depth: int, scope_filter: str | None
) -> AnalysisConfig:
    """Convert raw CLI inputs to validated analysis configuration.

    Args:
        file_path: Raw file path from CLI
        depth: Analysis depth
        scope_filter: Optional scope filter

    Returns:
        Validated analysis configuration
    """
    abs_file_path = convert_to_abs_path(file_path)

    return AnalysisConfig(
        file_path=abs_file_path, depth=depth, scope_filter=scope_filter
    )
