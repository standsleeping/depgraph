from pathlib import Path
from logging import Logger
from .import_crawler import ImportCrawler
from .dependency_graph import DependencyGraph
from typing import Dict, List


def crawl(
    abs_file_path: Path,
    logger: Logger,
) -> tuple[DependencyGraph, Dict[str, List[str]]]:
    """Crawl the import graph for the given entry file.

    Args:
        abs_file_path: The file to crawl
        logger: The logger to use

    Returns:
        A tuple containing:
        - DependencyGraph: The dependency graph of imported modules
        - dict: Unresolved imports categorized as local, system, and third-party
    """

    logger.info(f"Analyzing imports for {abs_file_path.name}")
    crawler = ImportCrawler(str(abs_file_path), logger)
    crawler.build_graph(str(abs_file_path))

    graph: DependencyGraph = crawler.graph

    # Get unresolved imports for JSON output
    unresolved_imports = crawler.get_unresolved_imports()

    return graph, unresolved_imports


