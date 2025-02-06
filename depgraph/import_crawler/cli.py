import argparse
from typing import Tuple


def parse_args() -> Tuple[str, str, str | None]:
    parser = argparse.ArgumentParser(
        description="Analyze Python file imports and create a dependency graph"
    )

    parser.add_argument(
        "entry_file",
        help="Path to the Python file to analyze",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

    parser.add_argument(
        "--log-file",
        help="Write logs to this file instead of stderr",
    )

    args = parser.parse_args()

    return args.entry_file, args.log_level, args.log_file
