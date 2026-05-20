"""
ml_pipeline/utils/logger.py
============================
Standardised logger factory for the ml_pipeline package.
"""

from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger namespaced under 'ml_pipeline.<name>'.

    Using a common prefix lets Django's LOGGING config capture all
    ml_pipeline loggers with a single 'ml_pipeline' entry.
    """
    return logging.getLogger(f"ml_pipeline.{name}")
