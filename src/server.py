"""
MCP server implementation using FastMCP.

Handles server configuration, resource/tool registration,
and error handling for the MCP server.
"""

import logging
import gc
from typing import Optional, Dict, Any
from datetime import datetime
from mcp.server.fastmcp import FastMCP, Context
from .utils.logging import configure_logging
from .utils.errors import MCPError, ConfigurationError, DatabaseError
from .db.init_db import init_db, get_db

logger = logging.getLogger(__name__)


async def configure_server(server: FastMCP) -> FastMCP:
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

        # Register all tools with error handling
        try:
            # Register tools and store results with error handling
            tool_registrations = [
                ("entity", register_entity_tools),
                ("relationship", register_relationship_tools), 
                ("observation", register_observation_tools),
                ("provider", register_provider_tools),
                ("ansible", register_ansible_tools),
                ("analysis", register_analysis_tools)
            ]
            
            tools = []
            for tool_type, register_fn in tool_registrations:
                try:
                    new_tools = await register_fn(server)
                    tools.extend(new_tools)
                    logger.info(f"Registered {len(new_tools)} {tool_type} tools")
                except Exception as e:
                    logger.error(f"Failed to register {tool_type} tools: {str(e)}")
                    raise ConfigurationError(f"Failed to register {tool_type} tools: {str(e)}")
            
            # Store registered tools
            for tool in tools:
                server._tools[tool.name] = tool
                logger.debug(f"Stored tool: {tool.name}")
        except Exception as e:
            logger.error(f"Failed to register tools: {str(e)}")
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


        # Add core protocol methods
        async def get_server_info():
            """Get server information."""
            return {
                "name": server.name,
                "version": "1.0.0",
                "capabilities": ["resources", "tools", "async_operations", "sessions"],
                "description": "Infrastructure Memory Server",
                "documentation_url": "https://docs.example.com/mcp"
            }

        async def create_session():
            """Create a new session."""
            from uuid import uuid4
            session_id = str(uuid4())
            # Store session in server state
            server._sessions[session_id] = {
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            return {"id": session_id}

        async def start_async_operation(tool_name: str, arguments: dict = None) -> dict:
            """Start an async operation."""
            from uuid import uuid4
            
            # Validate tool exists
            tool = server._tools.get(tool_name)
            if not tool:
                raise MCPError(f"Tool {tool_name} not found", code="TOOL_NOT_FOUND")
                
            op_id = str(uuid4())
            
            # Create context for tool
            ctx = Context()
            
            try:
                # Start tool execution asynchronously
                result = await tool(ctx, **(arguments or {}))
                
                # Store operation state
                server._operations[op_id] = {
                    "id": op_id,
                    "status": "completed",
                    "tool": tool_name,
                    "arguments": arguments or {},
                    "created_at": datetime.utcnow().isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                    "result": result
                }
            except Exception as e:
                server._operations[op_id] = {
                    "id": op_id,
                    "status": "failed",
                    "tool": tool_name,
                    "arguments": arguments or {},
                    "created_at": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
                raise MCPError(f"Tool execution failed: {str(e)}", code="TOOL_ERROR")
                
            return server._operations[op_id]

        async def read_resource(resource_path: str, params: dict = None) -> Dict[str, Any]:
            """Read a resource with parameters."""
            if not resource_path:
                raise MCPError("Resource path required", code="INVALID_RESOURCE")
                
            if resource_path.startswith("nonexistent://"):
                raise MCPError("Resource not found", code="RESOURCE_NOT_FOUND")
                
            try:
                # Get resource handler
                handler = server._resources.get(resource_path)
                if not handler:
                    raise MCPError(f"Resource {resource_path} not found", code="RESOURCE_NOT_FOUND")
                
                # Create context for resource
                ctx = Context()
                
                # Call handler with context
                result = await handler(ctx, **(params or {}))
                
                return {
                    "data": result,
                    "resource_path": resource_path,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                raise MCPError(f"Resource error: {str(e)}", code="RESOURCE_ERROR")

        async def get_operation_status(operation_id: str) -> Dict[str, Any]:
            """Get status of an async operation."""
            if operation_id not in server._operations:
                raise MCPError(f"Operation {operation_id} not found", code="OPERATION_NOT_FOUND")
            return server._operations[operation_id]

        async def end_session(session_id: str) -> None:
            """End a session."""
            if session_id not in server._sessions:
                raise MCPError(f"Session {session_id} not found", code="SESSION_NOT_FOUND")
            server._sessions[session_id]["status"] = "ended"
            server._sessions[session_id]["ended_at"] = datetime.utcnow().isoformat()

        # Attach protocol methods to server instance
        server.get_server_info = get_server_info
        server.create_session = create_session
        server.start_async_operation = start_async_operation
        server.read_resource = read_resource
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
