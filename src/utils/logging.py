"""
Logging configuration for MCP server.
"""

import logging
from logging.config import dictConfig
from typing import Dict, Any

from ..config import Config


def configure_logging() -> None:
    """Configure logging for the application."""
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": Config.LOG_FORMAT},
        },
        "handlers": {
            "default": {
                "level": Config.LOG_LEVEL,
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default"],
                "level": Config.LOG_LEVEL,
                "propagate": True,
            },
            "mcp_server": {
                "handlers": ["default"],
                "level": Config.LOG_LEVEL,
                "propagate": False,
            },
        },
    }

    dictConfig(logging_config)
