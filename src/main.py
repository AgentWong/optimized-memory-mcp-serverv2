#!/usr/bin/env python3
"""
Main entry point for the MCP Server.

Initializes and runs the MCP server with configured resources and tools
for infrastructure management.
"""
import os
import inspect
import logging
from mcp.server.fastmcp import FastMCP
from .server import configure_server
from .utils.errors import ConfigurationError
from .utils.logging import configure_logging
from .db.init_db import init_db

logger = logging.getLogger(__name__)


async def create_server() -> FastMCP:
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

        # Configure server with all components
        server = await configure_server(server)
        
        # Handle different server types and ensure initialization
        if inspect.iscoroutine(server):
            server = await server
        elif hasattr(server, "__anext__"):
            server = await server.__anext__()
        elif inspect.isasyncgen(server):
            async for s in server:
                server = s
                break

        # Ensure server is properly initialized
        if inspect.iscoroutine(server):
            server = await server

        # Initialize server if needed
        if hasattr(server, "initialize") and not hasattr(server, "read_resource"):
            await server.initialize()
        
        # Verify required methods exist
        required_methods = [
            'get_server_info',
            'create_session',
            'start_async_operation',
            'read_resource',
            'get_operation_status',
            'end_session'
        ]
        
        for method in required_methods:
            if not hasattr(server, method):
                raise ConfigurationError(f"Server missing required method: {method}")
            
        logger.info("MCP server created and configured successfully")
        return server

    except Exception as e:
        logger.error(f"Failed to create server: {str(e)}")
        raise ConfigurationError(f"Server initialization failed: {str(e)}")


def main() -> None:
    """Main entry point."""
    try:
        import asyncio
        server = asyncio.run(create_server())
        if hasattr(server, "__anext__"):
            server = asyncio.run(server.__anext__())
        logger.info("Starting MCP server")
        try:
            server.run()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
            asyncio.run(server.cleanup())
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            try:
                asyncio.run(server.cleanup())
            except Exception as cleanup_error:
                logger.error(f"Cleanup error during shutdown: {str(cleanup_error)}")
            raise
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        raise


if __name__ == "__main__":
    main()
