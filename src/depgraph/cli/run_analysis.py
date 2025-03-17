from depgraph.cli.parse_args import parse_args
from depgraph.logger.setup_logger import setup_logger
from depgraph.processors import process_file
from depgraph.formatters.print_analysis import print_analysis
from depgraph.data.file_analysis import FileAnalysis
from depgraph.data.scope_info import ScopeInfo
from depgraph.data.scope_name import ScopeName
from depgraph.processors.process_scope import process_scope
from depgraph.import_crawler.crawl import crawl

def run_analysis() -> None:
    (
        file_path,
        depth,
        log_level,
        log_file,
        scope_filter,
        display_options,
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

    logger.info(f"Analyzing file '{file_path}'")

    file_analysis: FileAnalysis = process_file(file_path=file_path, depth=depth)

    module_scope_info: ScopeInfo
    if scope_filter:
        module_scope_info = file_analysis.scopes[ScopeName(scope_filter)]
    else:
        module_scope_info = file_analysis.scopes[ScopeName("<module>")]

    assignments = process_scope(module_scope_info)

    logger.info("File analysis complete!")

    print_analysis(
        analysis=file_analysis,
        scope_filter=scope_filter,
        assignments=assignments,
    )

    crawl(
        file_path=file_path,
        display_options=display_options,
        output_file=output_file,
        output_format=output_format,
        logger=logger,
    )

    logger.info("Crawler analysis complete!")