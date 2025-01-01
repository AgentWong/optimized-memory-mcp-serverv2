"""
MCP server implementation using FastMCP.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .config import Config
from .utils.logging import configure_logging
from .utils.errors import MCPError, ConfigurationError
from .db.init_db import init_db

logger = logging.getLogger(__name__)

def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    try:
        # Configure logging
        configure_logging()
        
        # Initialize database
        init_db()
        
        # Create FastMCP instance
        server = FastMCP(
            "Optimized Memory MCP Server",
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
        
        # Register error handlers
        @server.exception_handler(MCPError)
        async def handle_mcp_error(error: MCPError) -> dict:
            logger.error(f"MCP error: {error.message}", extra={"details": error.details})
            return {
                "error": error.code,
                "message": error.message,
                "details": error.details
            }
        
        return server
        
    except Exception as e:
        raise ConfigurationError(f"Failed to create server: {str(e)}")

def get_server() -> Optional[FastMCP]:
    """Get the MCP server instance."""
    try:
        return create_server()
    except Exception as e:
        logger.error(f"Failed to get server: {str(e)}")
        return None
