"""
logger.py
Centralized application logging configuration.

Features:
    - Provides formatted stream loggers for system tracking and debugging
    - Prevents duplicate log handler attachments across module imports

Dependencies:
    - logging: Standard Python logging library

Exports:
    - get_logger(name): Configures and returns a named logger instance
"""

import logging



def get_logger(name: str) -> logging.Logger:
    """Configures and returns a named logging instance.

    Args:
        name: Name identifier for the logger instance (usually __name__).

    Returns:
        logging.Logger instance formatted with ISO timestamps and log levels.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger

