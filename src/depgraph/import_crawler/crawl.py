import os
import json
from logging import Logger
from .import_crawler import ImportCrawler
from .tree_printer import TreePrinter
from .module_info import ModuleInfo
from .dependency_graph import DependencyGraph
from typing import Set


def crawl(
    file_path: str,
    display_options: Set[str],
    logger: Logger,
) -> tuple[DependencyGraph, dict]:
    """Crawl the import graph for the given entry file.

    Args:
        file_path: The file to crawl
        display_options: The display options to use
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

    # Get unresolved imports for JSON output and print them
    unresolved_imports = crawler.get_unresolved_imports()
    crawler.print_unresolved_imports()

    # Handle console display options
    if "simple" in display_options:
        print("-" * 80)
        crawler.print_graph()
        print("-" * 80)

    if "tree" in display_options:
        if "simple" in display_options:
            print()  # Add spacing between formats
        printer = TreePrinter(graph.dependencies)
        root = ModuleInfo(file_path)
        print("Dependency Tree:")
        print(printer.tree(root))

    if "json" in display_options:
        if display_options != {"json"}:
            print()  # Add spacing between formats
        print("Dependency Graph (JSON):")
        json_graph = graph.to_json()
        print(json.dumps(json_graph, indent=2))

    return graph, unresolved_imports


