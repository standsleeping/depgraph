import argparse
from typing import Tuple, Set


def parse_args() -> Tuple[str, str, str | None, Set[str]]:
    """Parse command line arguments."""
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
        help="Display format(s) to use. Can specify multiple formats.",
    )

    args = parser.parse_args()

    # Convert display options to set
    display_options = set(args.display)
    if "all" in display_options:
        display_options = {"simple", "tree", "json"}

    return args.entry_file, args.log_level.upper(), args.log_file, display_options
