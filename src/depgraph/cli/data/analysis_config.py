from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnalysisConfig:
    """Configuration for file analysis."""

    file_path: Path
    depth: int
    scope_filter: str | None
