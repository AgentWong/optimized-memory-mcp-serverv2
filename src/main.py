#!/usr/bin/env python3
"""
Main entry point for the MCP Server.

Initializes and runs the MCP server with configured resources and tools
for infrastructure management.
"""
import os
from mcp.server.fastmcp import FastMCP
from .server import configure_server
from .utils.errors import ConfigurationError

def create_server() -> FastMCP:
    """Create and configure the MCP server instance."""
    if not os.getenv("DATABASE_URL"):
        raise ConfigurationError("DATABASE_URL environment variable is required")
        
    server = FastMCP(
        "Infrastructure Memory Server",
        dependencies=[
            "SQLAlchemy>=2.0.0",
            "alembic>=1.13.0",
            "uvx>=0.1.0"
        ]
    )
    configure_server(server)
    return server

def main() -> None:
    """Main entry point."""
    server = create_server()
    server.run()

if __name__ == "__main__":
    main()
