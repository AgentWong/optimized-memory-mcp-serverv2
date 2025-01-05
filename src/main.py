#!/usr/bin/env python3
"""
Main entry point for the MCP Server.

Initializes and runs the FastMCP server with configured resources and tools
for infrastructure management.
"""
import logging
import signal
import time
from typing import Optional
import asyncio
from datetime import datetime
from src.db.connection import get_db
from src.db.models.entities import Entity
from src.db.models.observations import Observation
from src.db.models.relationships import Relationship
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


def register_tools(mcp: FastMCP) -> None:
    """Register all tools with the MCP server."""
    
    @mcp.tool()
    def create_entity(name: str, entity_type: str, observations: list[str] = None) -> dict:
        """Create a new entity."""
        try:
            with get_db() as db:
                entity = Entity(
                    name=name,
                    entity_type=entity_type,
                    meta_data={},
                    tags={}
                )
                db.add(entity)
                db.commit()
                db.refresh(entity)
                
                # Add initial observations if provided
                if observations:
                    for obs in observations:
                        observation = Observation(
                            entity_id=entity.id,
                            type="initial",
                            observation_type="note", 
                            value={"text": obs},
                            meta_data={}
                        )
                        db.add(observation)
                    db.commit()
                
                return {
                    "id": str(entity.id),
                    "name": entity.name,
                    "entity_type": entity.entity_type,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat(),
                    "meta_data": entity.meta_data
                }
        except Exception as e:
            raise MCPError(
                message=f"Failed to create entity: {str(e)}",
                code="ENTITY_CREATE_ERROR",
                details={
                    "name": name,
                    "entity_type": entity_type,
                    "error": str(e)
                }
            )

    @mcp.tool()
    def create_relationship(
        source_id: int,
        target_id: int,
        relationship_type: str,
        metadata: dict = None
    ) -> dict:
        """Create a relationship between entities."""
        with get_db() as db:
            relationship = Relationship(
                source_id=source_id,
                target_id=target_id,
                type=relationship_type,
                relationship_type=relationship_type,
                meta_data=metadata or {}
            )
            db.add(relationship)
            db.commit()
            db.refresh(relationship)
            return relationship.to_dict()

def register_resources(mcp: FastMCP) -> None:
    """Register all resources with the MCP server."""
    
    @mcp.resource("entities://list")
    def list_entities() -> dict:
        """List all entities."""
        with get_db() as db:
            entities = db.query(Entity).all()
            return {
                "data": [e.to_dict() for e in entities],
                "resource_path": "entities://list",
                "timestamp": datetime.utcnow().isoformat()
            }

    @mcp.resource("entities://{id}")
    def get_entity(id: str) -> dict:
        """Get entity by ID."""
        with get_db() as db:
            entity = db.query(Entity).filter(Entity.id == id).first()
            if not entity:
                raise MCPError(
                    message=f"Entity not found: {id}",
                    code="RESOURCE_NOT_FOUND",
                    details={
                        "resource_id": id,
                        "resource_type": "entity"
                    }
                )
            return {
                "data": entity.to_dict(),
                "resource_path": f"entities://{id}",
                "timestamp": datetime.utcnow().isoformat()
            }

def create_server() -> FastMCP:
    """Create and configure the MCP server instance."""
    try:
        # Create FastMCP instance
        mcp = FastMCP(
            "Infrastructure Memory Server",
            dependencies=["sqlalchemy", "alembic", "redis", "asyncio", "aiohttp"]
        )

        # Register core functionality
        register_tools(mcp)
        register_resources(mcp)

        # Register module resources and tools
        from .resources import entities, relationships, observations, providers, ansible, versions
        from .tools import (
            entities as entity_tools,
            relationships as relationship_tools, 
            observations as observation_tools,
            providers as provider_tools,
            ansible as ansible_tools,
            analysis as analysis_tools
        )

        for module in [entities, relationships, observations, providers, ansible, versions]:
            module.register_resources(mcp)

        for module in [
            entity_tools, relationship_tools, observation_tools,
            provider_tools, ansible_tools, analysis_tools
        ]:
            module.register_tools(mcp)

        return mcp

    except Exception as e:
        logger.error(f"Failed to create server: {str(e)}", exc_info=True)
        raise MCPError(f"Server initialization failed: {str(e)}")


def shutdown() -> None:
    """Perform graceful shutdown."""
    global is_shutting_down
    if not is_shutting_down:
        is_shutting_down = True
        logger.info("Initiating graceful shutdown")
    try:
        mcp.shutdown()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


def main() -> None:
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
                    logger.error(
                        f"Database initialization failed after {max_retries} attempts: {str(e)}"
                    )
                    raise
                logger.warning(
                    f"Database initialization attempt {attempt + 1} failed: {str(e)}"
                )
                time.sleep(retry_delay)
                retry_delay *= 2

        # Import and register resources/tools
        from .resources import (
            entities,
            relationships,
            observations,
            providers,
            ansible,
            versions,
        )
        from .tools import (
            entities as entity_tools,
            relationships as relationship_tools,
            observations as observation_tools,
            providers as provider_tools,
            ansible as ansible_tools,
            analysis as analysis_tools,
        )

        # Register resources
        resource_modules = [
            entities,
            relationships,
            observations,
            providers,
            ansible,
            versions,
        ]

        for module in resource_modules:
            try:
                module.register_resources(mcp)
            except Exception as e:
                logger.error(
                    f"Failed to register resources from {module.__name__}: {str(e)}"
                )
                raise

        # Register tools
        tool_modules = [
            entity_tools,
            relationship_tools,
            observation_tools,
            provider_tools,
            ansible_tools,
            analysis_tools,
        ]

        logger.info("Registering tool modules...")
        registered_tools = 0
        validation_errors = []

        for i, module in enumerate(tool_modules, 1):
            if is_shutting_down:
                logger.info("Shutdown requested, stopping tool registration")
                break

            try:
                logger.debug(
                    f"Registering tools from {module.__name__} ({i}/{len(tool_modules)})"
                )
                tools = module.register_tools(mcp)
                if not tools:
                    tools = []  # Handle empty results

                if tools:
                    # Validate each tool
                    for tool in tools:
                        try:
                            if not hasattr(tool, "__doc__") or not tool.__doc__:
                                validation_errors.append(
                                    f"Tool {tool.__name__} missing documentation"
                                )
                            if not hasattr(tool, "__annotations__"):
                                validation_errors.append(
                                    f"Tool {tool.__name__} missing type hints"
                                )
                        except Exception as e:
                            validation_errors.append(
                                f"Error validating {tool.__name__}: {str(e)}"
                            )

                    registered_tools += len(tools)
                    logger.info(
                        f"Successfully registered {len(tools)} tools from {module.__name__}"
                    )
                else:
                    logger.warning(f"No tools registered from {module.__name__}")

            except MCPError as e:
                logger.error(
                    f"MCP error registering tools from {module.__name__}: {str(e)}"
                )
                if not is_shutting_down:
                    raise
            except Exception as e:
                logger.error(
                    f"Unexpected error registering tools from {module.__name__}: {str(e)}",
                    exc_info=True,
                )
                if not is_shutting_down:
                    raise

        if validation_errors:
            logger.warning("Tool validation warnings:")
            for error in validation_errors:
                logger.warning(f"  - {error}")

        logger.info(
            f"Tool registration complete. Total tools registered: {registered_tools}"
        )

        logger.info("Starting MCP server")
        try:
            mcp.run()
        except Exception as e:
            logger.error(f"Server runtime error: {str(e)}")
            raise

    except KeyboardInterrupt:
        shutdown()
    except MCPError as e:
        logger.error(f"MCP server error: {str(e)}")
        shutdown()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        shutdown()
        raise


if __name__ == "__main__":
    main()
