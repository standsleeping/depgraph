import argparse
from typing import Tuple, Optional, Set


def parse_args() -> Tuple[str, int, str, Optional[str], Optional[str], Set[str], Optional[str], Optional[str]]:
    """Parse command line arguments.

    Returns:
        Tuple containing:
        - entry_file: Path to the Python file to analyze
        - depth: Depth to analyze
        - log_level: Logging level to use
        - log_file: Optional path to log file
        - scope_filter: Optional scope name to filter the output
        - display_options: Set of display formats for console output
        - output_file: Optional path to write analysis results
        - output_format: Format for output file (defaults to 'json')
    """
    arg_description = "Analyze dependencies in Python code"
    parser = argparse.ArgumentParser(description=arg_description)

    parser.add_argument(
        "entry_file",
        help="Path to the Python file to analyze",
        type=str,
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=4,
        help="Depth of the analysis",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO"],
        default="INFO",
        help="Set the logging level",
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (if not specified, logs to stderr only)",
    )

    parser.add_argument(
        "--scope-filter",
        type=str,
        help="Filter output to a specific scope (e.g. '<module>.outer.Inner.method')",
    )

    parser.add_argument(
        "-d",
        "--display",
        choices=["simple", "tree", "json", "all"],
        default=["simple"],
        nargs="+",
        help="Display format(s) to use for console output. Can specify multiple formats.",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        help="Write analysis results to specified file",
    )

    parser.add_argument(
        "--output-format",
        choices=["json"],
        default="json",
        help="Format for output file (default: json)",
    )


    args = parser.parse_args()

    # Convert display options to set
    display_options = set(args.display)
    if "all" in display_options:
        display_options = {"simple", "tree", "json"}

    return (
        args.entry_file,
        args.depth,
        args.log_level,
        args.log_file,
        args.scope_filter,
        display_options,
        args.output_file,
        args.output_format,
    )
