import os
import json

from ..logger import setup_logger
from .import_crawler import ImportCrawler
from .tree_printer import TreePrinter
from .module_info import ModuleInfo
from .dependency_graph import DependencyGraph
from .cli import parse_args


def main() -> None:
    (
        entry_file,
        log_level,
        log_file,
        display_options,
        output_file,
        output_format,
    ) = parse_args()

    final_output_format = output_format if output_format is not None else "json"

    logger = setup_logger(level=log_level, log_file=log_file)

    logger.debug("Starting import analysis with parameters:")
    logger.debug(f"  entry_file: {entry_file}")
    logger.debug(f"  log_level: {log_level}")
    logger.debug(f"  log_file: {log_file}")
    logger.debug(f"  display_options: {display_options}")

    if output_file:
        logger.debug(f"  output_file: {output_file}")
        logger.debug(f"  output_format: {output_format}")

    logger.info(f"Analyzing imports for {os.path.basename(entry_file)}")
    crawler = ImportCrawler(entry_file, logger)
    crawler.build_graph(entry_file)

    graph: DependencyGraph = crawler.graph

    # Print unresolved imports
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
        root = ModuleInfo(entry_file)
        print("Dependency Tree:")
        print(printer.tree(root))

    if "json" in display_options:
        if display_options != {"json"}:
            print()  # Add spacing between formats
        print("Dependency Graph (JSON):")
        json_graph = graph.to_json()
        print(json.dumps(json_graph, indent=2))

    if output_file:
        write_output(graph, output_file, final_output_format)
        logger.info(f"Analysis results written to {output_file}")

    logger.info("Analysis complete!")


def write_output(graph: DependencyGraph, output_file: str, output_format: str) -> None:
    """Write analysis results to file in specified format.

    Args:
        graph: The dependency graph to output
        output_file: Path to output file
        output_format: Format to write (currently only 'json' supported)
    """
    if output_format == "json":
        json_data = graph.to_json()
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)


if __name__ == "__main__":
    main()
