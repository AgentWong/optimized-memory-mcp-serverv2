#!/usr/bin/env python3
"""
Main entry point for the MCP Server.

Initializes and runs the FastMCP server with configured resources and tools
for infrastructure management.
"""
import logging
import signal
import asyncio
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .utils.logging import configure_logging
from .db.init_db import init_db
from .utils.errors import MCPError

logger = logging.getLogger(__name__)

# Track server status
is_shutting_down = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global is_shutting_down
    if is_shutting_down:
        logger.warning("Forced shutdown requested, terminating immediately")
        raise SystemExit(1)
    logger.info(f"Received signal {signum}, initiating graceful shutdown")
    is_shutting_down = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Create FastMCP instance with capabilities
mcp = FastMCP(
    "Infrastructure Memory Server",
    dependencies=[
        "sqlalchemy",
        "alembic",
        "redis",
        "asyncio",
        "aiohttp"
    ],
    capabilities={
        "resources": {
            "subscribe": True,
            "listChanged": True
        },
        "tools": {
            "listChanged": True
        },
        "logging": True,
        "completion": True
    }
)

async def shutdown() -> None:
    """Perform graceful shutdown."""
    global is_shutting_down
    if not is_shutting_down:
        is_shutting_down = True
        logger.info("Initiating graceful shutdown")
    try:
        await mcp.shutdown()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

async def main() -> None:
    """Main entry point."""
    try:
        # Configure logging
        configure_logging()
        
        # Initialize database with retries
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                init_db()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Database initialization failed after {max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        
        # Import and register resources/tools
        from .resources import (
            entities, relationships, observations,
            providers, ansible, versions
        )
        from .tools import (
            entities as entity_tools,
            relationships as relationship_tools,
            observations as observation_tools,
            providers as provider_tools,
            ansible as ansible_tools,
            analysis as analysis_tools
        )

        # Register resources
        resource_modules = [
            entities, relationships, observations,
            providers, ansible, versions
        ]
        
        for module in resource_modules:
            try:
                module.register_resources(mcp)
            except Exception as e:
                logger.error(f"Failed to register resources from {module.__name__}: {str(e)}")
                raise

        # Register tools (async)
        tool_modules = [
            entity_tools, relationship_tools,
            observation_tools, provider_tools,
            ansible_tools, analysis_tools
        ]
        
        for module in tool_modules:
            try:
                await module.register_tools(mcp)
            except Exception as e:
                logger.error(f"Failed to register tools from {module.__name__}: {str(e)}")
                raise

        logger.info("Starting MCP server")
        try:
            await mcp.run_async()
        except Exception as e:
            logger.error(f"Server runtime error: {str(e)}")
            raise

    except KeyboardInterrupt:
        await shutdown()
    except MCPError as e:
        logger.error(f"MCP server error: {str(e)}")
        await shutdown()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        await shutdown()
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
