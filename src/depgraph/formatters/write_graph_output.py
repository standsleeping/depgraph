import os
import json
import logging
from depgraph.import_crawler.dependency_graph import DependencyGraph


def write_output(graph: DependencyGraph, output_file: str, output_format: str, logger: logging.Logger) -> None:
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
        logger.info(f"Output written to {output_file}")
    else:
        logger.error(f"Unsupported output format: {output_format}")
