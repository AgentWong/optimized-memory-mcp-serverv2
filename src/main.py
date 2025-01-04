#!/usr/bin/env python3
"""
Main entry point for the MCP Server.

Initializes and runs the MCP server with configured resources and tools
for infrastructure management.
"""
import os
import logging
from mcp.server.fastmcp import FastMCP
from .server import configure_server
from .utils.errors import ConfigurationError
from .utils.logging import configure_logging
from .db.init_db import init_db

logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Create and configure the MCP server instance."""
    # Configure logging first
    configure_logging()

    # Use test SQLite database if DATABASE_URL not set
    database_url = os.getenv("DATABASE_URL", "sqlite:///test.db")

    try:
        # Initialize database
        init_db()

        # Create and configure server
        server = FastMCP(
            "Infrastructure Memory Server",
            dependencies=[
                "SQLAlchemy>=2.0.0",
                "alembic>=1.13.0",
                "cachetools>=5.0.0",
            ],
        )
        configure_server(server)
        logger.info("MCP server created and configured successfully")
        return server

    except Exception as e:
        logger.error(f"Failed to create server: {str(e)}")
        raise ConfigurationError(f"Server initialization failed: {str(e)}")


def main() -> None:
    """Main entry point."""
    try:
        server = create_server()
        logger.info("Starting MCP server")
        server.run()
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        raise


if __name__ == "__main__":
    main()
