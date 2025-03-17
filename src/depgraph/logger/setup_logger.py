import logging
import os
import sys
from typing import Optional

DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"

DEBUG_FORMAT = (
    "%(asctime)s [%(levelname)s] [%(name)s] %(filename)s:%(lineno)d: %(message)s"
)


def setup_logger(
    name: str = "depgraph",
    level: str = "INFO",
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.

    Args:
        name: The name of the logger
        level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string (if None, uses default format)
        log_file: Path to log file (if None, logs to stderr only)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Clear any existing handlers
    logger.handlers.clear()

    # Prevent propagation to root logger
    logger.propagate = False

    # Set level on the logger itself
    logger.setLevel(getattr(logging, level.upper()))

    # Use debug format if level is DEBUG, otherwise use default
    fmt = log_format or (DEBUG_FORMAT if level.upper() == "DEBUG" else DEFAULT_FORMAT)
    formatter = logging.Formatter(fmt)

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)

    # Ensure handler level matches logger level
    console_handler.setLevel(getattr(logging, level.upper()))
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        # Ensure handler level matches logger level
        file_handler.setLevel(getattr(logging, level.upper()))
        logger.addHandler(file_handler)

    return logger


