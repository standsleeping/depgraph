import argparse
from typing import Tuple, Set, Optional


def parse_args() -> Tuple[
    str, str, Optional[str], Set[str], Optional[str], Optional[str]
]:
    """Parse command line arguments.

    Returns:
        Tuple containing:
        - entry_file: Python file to analyze
        - log_level: Logging level
        - log_file: Optional path to log file
        - display_options: Set of display formats for console output
        - output_file: Optional path to write analysis results
        - output_format: Format for output file (defaults to 'json')
    """
    parser = argparse.ArgumentParser(description="Analyze Python import dependencies.")

    parser.add_argument("entry_file", help="Python file to analyze")

    parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )

    parser.add_argument("--log-file", help="Log file to write to (optional)")

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
        args.log_level.upper(),
        args.log_file,
        display_options,
        args.output_file,
        args.output_format,
    )
