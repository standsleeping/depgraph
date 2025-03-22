import json
from pathlib import Path
from typing import Dict, Any
from depgraph.cli.parse_args import parse_args
from depgraph.logger.setup_logger import setup_logger
from depgraph.processors import process_file
from depgraph.formatters.write_graph_output import write_output
from depgraph.formatters.process_output import process_output
from depgraph.data.file_analysis import FileAnalysis
from depgraph.data.scope_info import ScopeInfo
from depgraph.data.scope_name import ScopeName
from depgraph.processors.process_scope import process_scope
from depgraph.import_crawler.crawl import crawl
from depgraph.tools.convert_to_abs_path import convert_to_abs_path

def run_analysis() -> None:
    (
        file_path,
        depth,
        log_level,
        log_file,
        scope_filter,
        output_file,
        output_format,
    ) = parse_args()

    logger = setup_logger(level=log_level, log_file=log_file)
    logger.debug("Starting analysis with parameters:")
    logger.debug(f"  file_path: {file_path}")
    logger.debug(f"  depth: {depth}")
    logger.debug(f"  log_level: {log_level}")
    logger.debug(f"  log_file: {log_file}")

    if scope_filter:
        logger.debug(f"  scope_filter: {scope_filter}")

    if output_file:
        logger.debug(f"  output_file: {output_file}")
        logger.debug(f"  output_format: {output_format}")

    logger.info(f"Converting file path to absolute path: {file_path}")

    abs_file_path: Path = convert_to_abs_path(file_path)

    logger.info(f"Analyzing file '{abs_file_path}'")

    file_analysis: FileAnalysis = process_file(abs_file_path=abs_file_path, depth=depth)

    module_scope_info: ScopeInfo
    if scope_filter:
        module_scope_info = file_analysis.scopes[ScopeName(scope_filter)]
    else:
        module_scope_info = file_analysis.scopes[ScopeName("<module>")]

    assignments = process_scope(module_scope_info)

    logger.info("File analysis complete!")

    output: Dict[str, Any] = process_output(
        analysis=file_analysis,
        scope_filter=scope_filter,
        assignments=assignments,
    )

    graph, unresolved_imports = crawl(
        abs_file_path=abs_file_path,
        logger=logger,
    )

    json_graph = graph.to_json()

    output["graph"] = json_graph
    output["unresolved_imports"] = unresolved_imports

    logger.info("Analysis complete!")

    if output_file and output_format:
        write_output(output, output_file, output_format, logger)
    else:
        # indent the output
        print(json.dumps(output, indent=4))

