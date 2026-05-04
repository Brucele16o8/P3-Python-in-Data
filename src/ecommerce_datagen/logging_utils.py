from __future__ import annotations

import logging

from rich.logging import RichHandler


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure Rich-based application logging and return the project logger."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
        force=True,
    )
    return logging.getLogger("ecommerce_datagen")
