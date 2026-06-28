"""
Centralized logging configuration.

Why structured logging matters in production specifically: locally, you
can just watch the terminal scroll by. In production, your only window
into what's happening is whatever your hosting platform's log viewer
shows you -- there's no terminal to glance at. Without deliberate
logging, a failure in production is nearly invisible until a user
reports it.

We use Python's built-in logging module (no new dependency) configured
to write structured, leveled messages -- INFO for normal operation
milestones, WARNING for recoverable issues, ERROR for failures that need
attention.
"""

import logging
import sys

from app.core.config import settings


def setup_logging():
    """
    Configure the root logger once, at application startup. Called from
    main.py before the app starts serving requests.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Quiet down noisy third-party loggers that would otherwise flood
    # production logs with low-value detail (e.g. every HTTP connection
    # detail from underlying libraries).
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger scoped to a specific module, e.g.
    get_logger(__name__) at the top of any file. The module name appears
    in every log line, making it obvious WHERE in the codebase a given
    log message came from.
    """
    return logging.getLogger(name)
