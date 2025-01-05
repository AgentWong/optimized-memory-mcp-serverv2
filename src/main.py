#!/usr/bin/env python3
"""
Main entry point for the MCP Server.

Initializes and runs the MCP server with configured resources and tools
for infrastructure management.
"""
import os
import asyncio
import logging
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from .server import configure_server
from .utils.errors import ConfigurationError
from .utils.logging import configure_logging
from .db.init_db import init_db

logger = logging.getLogger(__name__)


async def create_server() -> Server:
    """Create and configure the MCP server instance."""
    try:
        # Configure logging first
        configure_logging()

        # Initialize database
        init_db()

        # Create base server
        server = Server("Infrastructure Memory Server")

        # Configure server with all components
        configured_server = await configure_server(server)

        # Initialize the server
        init_options = InitializationOptions(
            server_name="Infrastructure Memory Server",
            server_version="1.0.0",
            capabilities=configured_server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )

        await configured_server.initialize(init_options)
        
        # Verify server has required methods
        if not hasattr(configured_server, 'read_resource'):
            raise ConfigurationError("Server missing read_resource method")
        if not hasattr(configured_server, 'call_tool'):
            raise ConfigurationError("Server missing call_tool method")
        if not hasattr(configured_server, 'start_async_operation'):
            raise ConfigurationError("Server missing start_async_operation method")
            
        return configured_server

    except Exception as e:
        logger.error(f"Failed to create server: {str(e)}")
        raise ConfigurationError(f"Server initialization failed: {str(e)}")


async def run_server(server: Server):
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

def main() -> None:
    """Main entry point."""
    try:
        server = asyncio.run(create_server())
        logger.info("Starting MCP server")
        try:
            asyncio.run(run_server(server))
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        raise


if __name__ == "__main__":
    main()
