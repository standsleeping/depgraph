import os
import json

from ..logger import setup_logger
from .import_crawler import ImportCrawler
from .tree_printer import TreePrinter
from .module_info import ModuleInfo
from .dependency_graph import DependencyGraph
from .cli import parse_args


def main() -> None:
    entry_file, log_level, log_file, display_options = parse_args()

    logger = setup_logger(level=log_level, log_file=log_file)

    logger.debug("Starting import analysis with parameters:")
    logger.debug(f"  entry_file: {entry_file}")
    logger.debug(f"  log_level: {log_level}")
    logger.debug(f"  log_file: {log_file}")
    logger.debug(f"  display_options: {display_options}")

    logger.info(f"Analyzing imports for {os.path.basename(entry_file)}")
    crawler = ImportCrawler(entry_file, logger)
    crawler.build_graph(entry_file)

    graph: DependencyGraph = crawler.graph

    # Simple format (original)
    if "simple" in display_options:
        print("-" * 80)
        crawler.print_graph()
        print("-" * 80)

    # Tree format
    if "tree" in display_options:
        if "simple" in display_options:
            print()  # Add spacing between formats
        printer = TreePrinter(graph.dependencies)
        root = ModuleInfo(entry_file)
        print("Dependency Tree:")
        print(printer.tree(root))

    # JSON format
    if "json" in display_options:
        if display_options != {"json"}:
            print()  # Add spacing between formats
        print("Dependency Graph (JSON):")
        json_graph = graph.to_json()
        print(json.dumps(json_graph, indent=2))

    logger.info("Analysis complete!")


if __name__ == "__main__":
    main()
