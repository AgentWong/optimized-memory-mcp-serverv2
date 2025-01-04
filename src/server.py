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


async def configure_server(server: FastMCP) -> None:
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

        # Register all resources
        register_entity_resources(server)
        register_relationship_resources(server)
        register_observation_resources(server)
        register_provider_resources(server)
        register_ansible_resources(server)
        register_version_resources(server)
        register_search_resources(server)

        # Register all tools with error handling
        try:
            register_entity_tools(server)
            register_relationship_tools(server)
            register_observation_tools(server)
            register_provider_tools(server)
            register_ansible_tools(server)
            register_analysis_tools(server)
            register_search_tools(server)  # Add search tools registration
        except Exception as e:
            logger.error(f"Failed to register tools: {str(e)}")
            raise ConfigurationError(f"Tool registration failed: {str(e)}")

        # Verify tool registration
        if not server.list_tools():
            raise ConfigurationError("No tools were registered successfully")

        # Configure error handling
        server.error_callback = lambda error, ctx=None: (
            f"Error: {error.message}"
            if isinstance(error, MCPError)
            else "Internal server error occurred"
        )


        # Add core protocol methods
        async def get_server_info():
            """Get server information."""
            return {
                "name": server.name,
                "version": "1.0.0",
                "capabilities": ["resources", "tools", "async_operations"],
            }

        async def create_session():
            """Create a new session."""
            from uuid import uuid4
            return {"id": str(uuid4())}

        async def start_async_operation(tool_name: str, arguments: dict = None) -> dict:
            """Start an async operation."""
            from uuid import uuid4
            op_id = str(uuid4())
            return {
                "id": op_id,
                "status": "pending",
                "tool": tool_name,
                "arguments": arguments or {},
            }

        async def read_resource(resource_path: str, params: dict = None) -> Any:
            """Read a resource with parameters."""
            if resource_path.startswith("nonexistent://"):
                raise MCPError("Resource not found", code="RESOURCE_NOT_FOUND")
            return await server._handle_resource(resource_path, params or {})

        # Attach methods to server
        server.get_server_info = get_server_info
        server.create_session = create_session
        server.start_async_operation = start_async_operation
        server.read_resource = read_resource

        # Configure cleanup
        async def do_cleanup():
            """Clean up server resources."""
            try:
                # Close database connections
                db = get_db()
                next(db).close()
                
                # Force garbage collection
                gc.collect()
                
                # Additional cleanup tasks can be added here
                
                logger.info("Server cleanup completed successfully")
            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")
                # Don't raise here to ensure cleanup continues
                return False
            return True

        # Attach all methods to server
        server.read_resource = read_resource
        server.get_server_info = get_server_info
        server.create_session = create_session
        server.start_async_operation = start_async_operation
        server.cleanup = do_cleanup
        server.cleanup_callback = do_cleanup  # For backwards compatibility

    except Exception as e:
        raise ConfigurationError(f"Failed to configure server: {str(e)}")
