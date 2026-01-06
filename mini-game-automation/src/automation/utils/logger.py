"""
Logging configuration for the automation tool.

Provides structured logging with table_id and timestamps
following the format: [LEVEL] [TIMESTAMP] [MODULE] [TABLE_ID] Message
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Log format following architecture specification
LOG_FORMAT = "[%(levelname)s] [%(timestamp)s] [%(module)s] [%(table_id)s] %(message)s"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"


class TableContextFilter(logging.Filter):
    """Filter that adds table_id and timestamp to log records."""

    def __init__(self, default_table_id: str = "-"):
        super().__init__()
        self.default_table_id = default_table_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Add table_id and formatted timestamp to log record."""
        if not hasattr(record, "table_id"):
            record.table_id = self.default_table_id
        if not hasattr(record, "timestamp"):
            record.timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        return True


class TableLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that automatically includes table_id in messages."""

    def __init__(self, logger: logging.Logger, table_id: int):
        super().__init__(logger, {"table_id": str(table_id)})
        self.table_id = table_id

    def process(self, msg: str, kwargs: dict) -> tuple:
        """Add table_id to extra dict."""
        extra = kwargs.get("extra", {})
        extra["table_id"] = str(self.table_id)
        extra["timestamp"] = datetime.now().strftime(TIMESTAMP_FORMAT)
        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Whether to output to console
    """
    # Create root logger
    root_logger = logging.getLogger("automation")
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Add table context filter
    context_filter = TableContextFilter()

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        console_handler.addFilter(context_filter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)


def get_logger(module_name: str, table_id: Optional[int] = None) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        module_name: Name of the module requesting the logger
        table_id: Optional table ID for table-specific logging

    Returns:
        Logger instance (or LoggerAdapter if table_id provided)
    """
    logger = logging.getLogger(f"automation.{module_name}")

    if table_id is not None:
        return TableLoggerAdapter(logger, table_id)

    return logger


def log_with_table(
    logger: logging.Logger,
    level: int,
    message: str,
    table_id: int,
    **kwargs,
) -> None:
    """
    Log a message with table_id context.

    Args:
        logger: Logger instance
        level: Logging level
        message: Log message
        table_id: Table ID for context
        **kwargs: Additional context to include
    """
    extra = {
        "table_id": str(table_id),
        "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
        **kwargs,
    }
    logger.log(level, message, extra=extra)


def log_error_with_screenshot(
    logger: logging.Logger,
    message: str,
    table_id: int,
    screenshot_path: Optional[Path] = None,
    error_type: str = "unknown",
    **context,
) -> None:
    """
    Log an error with optional screenshot path for debugging.

    Args:
        logger: Logger instance
        message: Error message
        table_id: Table ID
        screenshot_path: Path to error screenshot (if any)
        error_type: Type of error for categorization
        **context: Additional context information
    """
    extra = {
        "table_id": str(table_id),
        "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
        "error_type": error_type,
        "screenshot_path": str(screenshot_path) if screenshot_path else None,
        **context,
    }

    full_message = f"{message}"
    if screenshot_path:
        full_message += f" (Screenshot: {screenshot_path})"

    logger.error(full_message, extra=extra)
