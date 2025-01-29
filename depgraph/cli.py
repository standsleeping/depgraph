import argparse
from typing import Tuple, Optional


def parse_args() -> Tuple[str, int, str, Optional[str], Optional[str]]:
    """Parse command line arguments for function call analysis.

    Returns:
        Tuple containing:
        - file_path: Path to the Python file to analyze
        - depth: Depth to analyze
        - log_level: Logging level to use
        - log_file: Optional path to log file
        - scope_filter: Optional scope name to filter the output
    """
    arg_description = "Analyze dependencies in Python code"
    parser = argparse.ArgumentParser(description=arg_description)

    parser.add_argument(
        "file_path",
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
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
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

    args = parser.parse_args()

    return (
        args.file_path,
        args.depth,
        args.log_level,
        args.log_file,
        args.scope_filter,
    )
