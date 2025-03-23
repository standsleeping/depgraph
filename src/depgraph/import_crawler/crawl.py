from pathlib import Path
from .import_crawler import ImportCrawler
from .dependency_graph import DependencyGraph
from typing import Dict, List
from depgraph.logging import get_logger

logger = get_logger(__name__)


def crawl(
    abs_file_path: Path,
) -> tuple[DependencyGraph, Dict[str, List[str]]]:
    """Crawl the import graph for the given entry file.

    Args:
        abs_file_path: The file to crawl

    Returns:
        A tuple containing:
        - DependencyGraph: The dependency graph of imported modules
        - dict: Unresolved imports categorized as local, system, and third-party
    """

    logger.info(f"Analyzing imports for {abs_file_path.name}")
    crawler = ImportCrawler(abs_file_path)
    crawler.build_graph(abs_file_path)

    graph: DependencyGraph = crawler.graph

    # Get unresolved imports for JSON output
    unresolved_imports = crawler.get_unresolved_imports()

    return graph, unresolved_imports


