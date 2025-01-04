"""
MCP server implementation using FastMCP.

Handles server configuration, resource/tool registration,
and error handling for the MCP server.
"""

import logging
import gc
from typing import Optional
from mcp.server.fastmcp import FastMCP, Context
from .utils.logging import configure_logging
from .utils.errors import MCPError, ConfigurationError, DatabaseError
from .db.init_db import init_db, get_db

logger = logging.getLogger(__name__)


def configure_server(server: FastMCP) -> None:
    """
    Configure the MCP server with resources and tools.

    Sets up:
    - Logging configuration
    - Database initialization
    - Error handling
    - Resource cleanup
    """
    try:
        # Configure logging
        configure_logging()

        # Initialize database
        init_db()

        # Register resources and tools
        from .resources.entities import register_resources as register_entity_resources
        from .resources.relationships import (
            register_resources as register_relationship_resources,
        )
        from .resources.observations import (
            register_resources as register_observation_resources,
        )
        from .resources.providers import (
            register_resources as register_provider_resources,
        )
        from .resources.ansible import register_resources as register_ansible_resources
        from .resources.versions import register_resources as register_version_resources
        from .resources.search import register_resources as register_search_resources
        from .tools.entities import register_tools as register_entity_tools
        from .tools.relationships import register_tools as register_relationship_tools
        from .tools.observations import register_tools as register_observation_tools
        from .tools.providers import register_tools as register_provider_tools
        from .tools.ansible import register_tools as register_ansible_tools
        from .tools.analysis import register_tools as register_analysis_tools

        register_entity_resources(server)
        register_relationship_resources(server)
        register_observation_resources(server)
        register_provider_resources(server)
        register_ansible_resources(server)
        register_version_resources(server)
        register_search_resources(server)
        register_entity_tools(server)
        register_relationship_tools(server)
        register_observation_tools(server)
        register_provider_tools(server)
        register_ansible_tools(server)
        register_analysis_tools(server)

        # Register error handler
        @server.error_handler()
        def handle_error(error: Exception, ctx: Optional[Context] = None) -> str:
            if isinstance(error, MCPError):
                logger.error(
                    f"MCP error: {error.message}",
                    extra={"code": error.code, "details": error.details},
                )
                return f"Error: {error.message}"

            logger.error(f"Unexpected error: {str(error)}")
            return "Internal server error occurred"

        # Register cleanup handler
        @server.cleanup_handler()
        def cleanup(ctx: Optional[Context] = None) -> None:
            """Cleanup resources after request processing."""
            try:
                # Close any open database connections
                db = get_db()
                next(db).close()

                # Force garbage collection
                gc.collect()

            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")
                raise DatabaseError("Failed to cleanup resources")

    except Exception as e:
        raise ConfigurationError(f"Failed to configure server: {str(e)}")
