"""
Environment configuration for MCP server.
"""

import os
from typing import Any, Dict


class Config:
    """Server configuration settings."""

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mcp_server.db")

    # Server
    HOST = os.getenv("MCP_HOST", "127.0.0.1")
    PORT = int(os.getenv("MCP_PORT", "8000"))
    DEBUG = os.getenv("MCP_DEBUG", "0").lower() in ("true", "1", "t")

    # Logging
    LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            key: value for key, value in cls.__dict__.items() if not key.startswith("_")
        }

def load_environment() -> None:
    """Load environment configuration."""
    Config()  # Initialize config with environment variables
