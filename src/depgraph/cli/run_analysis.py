import logging
from depgraph.cli.parse_args import parse_args
from depgraph.logging import configure_logging, get_logger
from depgraph.cli.functions.analyze_file import analyze_file
from depgraph.cli.functions.handle_output import handle_output

logger = get_logger(__name__)


def run_analysis() -> None:
    (
        file_path,
        depth,
        parsed_log_level,
        scope_filter,
        output_file,
        output_format,
    ) = parse_args()

    log_level = getattr(logging, parsed_log_level)
    configure_logging(level=log_level)
    logger.debug("Starting analysis with parameters:")
    logger.debug(f"  file_path: {file_path}")
    logger.debug(f"  depth: {depth}")
    logger.debug(f"  log_level: {log_level}")

    if scope_filter:
        logger.debug(f"  scope_filter: {scope_filter}")

    if output_file:
        logger.debug(f"  output_file: {output_file}")
        logger.debug(f"  output_format: {output_format}")

    logger.info(f"Analyzing file '{file_path}'")

    analysis_result = analyze_file(
        file_path=file_path, depth=depth, scope_filter=scope_filter
    )

    logger.info("Analysis complete!")

    handle_output(
        analysis_result=analysis_result,
        output_file=output_file,
        output_format=output_format,
    )
