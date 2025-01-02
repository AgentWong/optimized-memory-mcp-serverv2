#!/usr/bin/env python3
"""
Main entry point for the MCP Server.
"""
from argparse import ArgumentParser
from mcp.server.fastmcp import FastMCP

def parse_arguments():
    """Parse command line arguments."""
    parser = ArgumentParser(description="MCP Server")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    # Add more arguments as needed
    return parser.parse_args()

def create_server():
    """Create and configure the MCP server instance."""
    server = FastMCP(
        "Optimized Memory MCP Server",
        dependencies=[
            "SQLAlchemy>=2.0.0",
            "alembic>=1.13.0",
            "fastapi>=0.109.0",
            "pydantic>=2.5.0"
        ]
    )
    
    # Configure server here
    from .server import configure_server
    configure_server(server)
    
    return server

def main():
    """Main entry point."""
    args = parse_arguments()
    server = create_server()
    
    # Get the ASGI application
    app = server.get_application()
    
    # The application will be run by uvx
    return app

if __name__ == "__main__":
    main()
