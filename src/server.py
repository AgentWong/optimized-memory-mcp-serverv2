"""
MCP server implementation using FastMCP.

Handles server configuration, resource/tool registration,
and error handling for the MCP server.
"""

import logging
import gc
import inspect
from typing import Optional, Dict, Any
from datetime import datetime
from mcp.server.lowlevel import Server
import mcp.types as types
from mcp.server.fastmcp import Context
from .utils.logging import configure_logging
from .utils.errors import MCPError, ConfigurationError, DatabaseError
from .db.init_db import init_db, get_db

logger = logging.getLogger(__name__)


async def configure_server(server: Server) -> Server:
    """
    Configure the MCP server with resources and tools.

    Sets up:
    - Logging configuration
    - Database initialization
    - Error handling
    - Resource cleanup
    - Session management
    - Async operation tracking
    """
    # Initialize server state
    server._sessions = {}
    server._operations = {}
    server._tools = {}  # Track registered tools
    server._resources = {}  # Track registered resources
    try:
        # Configure logging
        configure_logging()

        # Initialize database
        init_db()

        # Initialize server collections
        server._resources = {}  # Resource handlers
        server._tools = {}     # Tool handlers 
        server._sessions = {}  # Active sessions
        server._operations = {} # Async operations

        # Import registration functions
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

        # Register all resources
        for module in [entities, relationships, observations, providers, ansible, versions]:
            try:
                resources = await module.register_resources(server)
                if resources:
                    for resource in resources:
                        if callable(resource):
                            server._resources[resource.__name__] = resource
                logger.info(f"Registered resources from {module.__name__}")
            except Exception as e:
                logger.error(f"Failed to register resources from {module.__name__}: {str(e)}")
                raise ConfigurationError(f"Resource registration failed: {str(e)}")

        # Register all tools
        tool_modules = [
            entity_tools, relationship_tools, observation_tools,
            provider_tools, ansible_tools, analysis_tools
        ]
        
        for module in tool_modules:
            try:
                tools = await module.register_tools(server)
                if tools:  # Some modules might return None
                    for tool in tools:
                        if callable(tool):
                            server._tools[tool.__name__] = tool
                logger.info(f"Registered tools from {module.__name__}")
            except Exception as e:
                logger.error(f"Failed to register tools from {module.__name__}: {str(e)}")
                raise ConfigurationError(f"Tool registration failed: {str(e)}")

        # Verify tool registration
        tools = await server.list_tools()
        if not tools:
            raise ConfigurationError("No tools were registered successfully")

        # Configure error handling
        server.error_callback = lambda error, ctx=None: (
            f"Error: {error.message}"
            if isinstance(error, MCPError)
            else "Internal server error occurred"
        )


        # Register protocol handlers
        async def handle_read_resource(resource_path: str, params: dict = None) -> types.ReadResourceResult:
            """Handle resource reading requests."""
            if not resource_path:
                raise MCPError("Resource path required", code="INVALID_RESOURCE")
            handler = server._resources.get(resource_path)
            if not handler:
                raise MCPError(f"Resource {resource_path} not found", code="RESOURCE_NOT_FOUND")
            ctx = Context()
            result = await handler(ctx, **(params or {}))
            return types.ReadResourceResult(data=result, resource_path=resource_path)

        async def handle_call_tool(tool_name: str, arguments: dict = None) -> types.CallToolResult:
            """Handle tool execution requests."""
            tool = server._tools.get(tool_name)
            if not tool:
                raise MCPError(f"Tool {tool_name} not found", code="TOOL_NOT_FOUND")
            ctx = Context()
            result = await tool(ctx, **(arguments or {}))
            return types.CallToolResult(result=result)

        async def handle_start_async_operation(tool_name: str, arguments: dict = None) -> dict:
            """Handle async operation requests."""
            tool = server._tools.get(tool_name)
            if not tool:
                raise MCPError(f"Tool {tool_name} not found", code="TOOL_NOT_FOUND")
            ctx = Context()
            result = await tool(ctx, **(arguments or {}))
            return {"status": "completed", "result": result}

        # Register protocol handlers
        async def handle_read_resource(resource_path: str, params: dict = None) -> types.ReadResourceResult:
            """Handle resource reading requests."""
            if not resource_path:
                raise MCPError("Resource path required", code="INVALID_RESOURCE")
            handler = server._resources.get(resource_path)
            if not handler:
                raise MCPError(f"Resource {resource_path} not found", code="RESOURCE_NOT_FOUND")
            ctx = Context()
            result = await handler(ctx, **(params or {}))
            return types.ReadResourceResult(data=result, resource_path=resource_path)

        async def handle_call_tool(tool_name: str, arguments: dict = None) -> types.CallToolResult:
            """Handle tool execution requests."""
            tool = server._tools.get(tool_name)
            if not tool:
                raise MCPError(f"Tool {tool_name} not found", code="TOOL_NOT_FOUND")
            ctx = Context()
            result = await tool(ctx, **(arguments or {}))
            return types.CallToolResult(result=result)

        async def handle_start_async_operation(tool_name: str, arguments: dict = None) -> dict:
            """Handle async operation requests."""
            tool = server._tools.get(tool_name)
            if not tool:
                raise MCPError(f"Tool {tool_name} not found", code="TOOL_NOT_FOUND")
            ctx = Context()
            result = await tool(ctx, **(arguments or {}))
            return {"status": "completed", "result": result}

        # Attach handlers directly to server instance
        server.read_resource = handle_read_resource
        server.call_tool = handle_call_tool
        server.start_async_operation = handle_start_async_operation

        # Ensure handlers are properly bound
        if not hasattr(server, 'read_resource'):
            raise ConfigurationError("Failed to attach read_resource handler")
        if not hasattr(server, 'call_tool'):
            raise ConfigurationError("Failed to attach call_tool handler")
        if not hasattr(server, 'start_async_operation'):
            raise ConfigurationError("Failed to attach start_async_operation handler")

        # Attach protocol methods to server instance
        server.get_server_info = get_server_info
        server.create_session = create_session
        server.get_operation_status = get_operation_status
        server.end_session = end_session
        
        # Configure cleanup and shutdown
        async def do_cleanup():
            """Clean up server resources."""
            try:
                # Clean up sessions
                for session_id in list(server._sessions.keys()):
                    if server._sessions[session_id]["status"] == "active":
                        try:
                            await end_session(session_id)
                        except Exception as e:
                            logger.error(f"Error ending session {session_id}: {str(e)}")
                
                # Clean up operations
                server._operations.clear()
                
                # Close database connections
                try:
                    db = get_db()
                    next(db).close()
                except Exception as e:
                    logger.error(f"Error closing database: {str(e)}")
                
                # Force garbage collection
                gc.collect()
                
                logger.info("Server cleanup completed successfully")
                return True
            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")
                return False

        # Attach cleanup methods
        server.cleanup = do_cleanup
        server.cleanup_callback = do_cleanup  # For backwards compatibility

        return server

    except Exception as e:
        raise ConfigurationError(f"Failed to configure server: {str(e)}")
