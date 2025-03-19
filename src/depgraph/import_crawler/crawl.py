import os
from logging import Logger
from .import_crawler import ImportCrawler
from .dependency_graph import DependencyGraph
from typing import Dict, List


def crawl(
    file_path: str,
    logger: Logger,
) -> tuple[DependencyGraph, Dict[str, List[str]]]:
    """Crawl the import graph for the given entry file.

    Args:
        file_path: The file to crawl
        logger: The logger to use

    Returns:
        A tuple containing:
        - DependencyGraph: The dependency graph of imported modules
        - dict: Unresolved imports categorized as local, system, and third-party
    """

    logger.info(f"Analyzing imports for {os.path.basename(file_path)}")
    crawler = ImportCrawler(file_path, logger)
    crawler.build_graph(file_path)

    graph: DependencyGraph = crawler.graph

    # Get unresolved imports for JSON output
    unresolved_imports = crawler.get_unresolved_imports()

    return graph, unresolved_imports


