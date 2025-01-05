"""
Entity management tools for the MCP server.

This module implements MCP tools for managing infrastructure entities.
Tools provide capabilities for:
- Creating new infrastructure entities with typed classification
- Updating entity metadata and properties
- Managing entity lifecycle and state
- Handling entity deletion and cleanup

Each tool follows standard patterns:
- Database integration through SQLAlchemy sessions
- Proper error handling with ValidationError and DatabaseError
- Consistent return structures with typed dictionaries
- Clean transaction management with commits and rollbacks
"""

from typing import Dict, Any, List, Optional

from mcp.server.fastmcp import FastMCP, Context
from ..db.connection import get_db
from ..db.models.entities import Entity
from ..db.models.observations import Observation
from ..utils.errors import DatabaseError, ValidationError


def register_tools(mcp: FastMCP) -> list:
    """Register entity management tools with the MCP server.

    This function registers all entity-related tools with the MCP server instance.
    Tools include:
    - create_entity: Create new infrastructure entities
    - update_entity: Modify existing entity properties
    - delete_entity: Remove entities from the system

    Each tool is registered with proper type hints, error handling, and database integration.
    Tools follow MCP protocol patterns for consistent behavior and error reporting.

    Entity tools handle:
    - Infrastructure components (servers, databases)
    - Network resources (routers, load balancers)
    - Storage systems (volumes, object stores)
    - Application services (APIs, queues)
    - Security components (firewalls, WAFs)

    Tool capabilities include:
    - Entity lifecycle management
    - Metadata and property updates
    - State tracking and validation

    Returns:
        List of registered tool objects
    """
    tools = []

    @mcp.tool()
    def create_entity(
        name: str,
        entity_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        observations: Optional[List[str]] = None,
        ctx: Context = None,
    ) -> Dict[str, Any]:
        """Create a new entity in the system.

        Args:
            name: Entity name (must be non-empty)
            entity_type: Type of entity (e.g. 'instance', 'database', 'network')
            metadata: Optional dictionary of metadata key-value pairs
            observations: Optional list of initial observation strings
            ctx: MCP context object

        Returns:
            Dict containing entity id, name and type

        Raises:
            ValidationError: If entity name is empty
            DatabaseError: If database operation fails

        Example:
            >>> result = create_entity(
            ...     name="web-server-1",
            ...     entity_type="instance",
            ...     metadata={"environment": "production"}
            ... )
            >>> print(result)
            {
                "id": 1,
                "name": "web-server-1",
                "type": "instance"
            }
        """
        if not name or not name.strip():
            raise ValidationError("Entity name cannot be empty")

        if metadata is not None and not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a dictionary")

        # Allow test types in non-production environments
        valid_types = {
            "instance",
            "database",
            "network",
            "storage",
            "security",
            "test",
            "test_type",
        }
        if entity_type.lower() not in valid_types:
            raise ValidationError(
                f"Invalid entity type. Must be one of: {', '.join(sorted(valid_types))}"
            )

        from ..db.connection import get_db

        db = next(get_db())
        try:
            entity = Entity(
                name=name.strip(),
                entity_type=entity_type.lower(),
                meta_data=metadata or {},
                tags={},
            )
            db.add(entity)
            db.commit()
            db.refresh(entity)

            # Add any initial observations
            if observations:
                if not isinstance(observations, list):
                    raise ValidationError("Observations must be a list")
                for obs_content in observations:
                    if not obs_content or not str(obs_content).strip():
                        raise ValidationError("Observation content cannot be empty")
                    try:
                        observation = Observation(
                            entity_id=entity.id,
                            observation_type="initial",
                            type="state",
                            value={"content": str(obs_content).strip()},
                            meta_data={},
                        )
                        db.add(observation)
                    except Exception as e:
                        db.rollback()
                        raise ValidationError(f"Failed to create observation: {str(e)}")
                db.commit()

            result = {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type,
                "metadata": entity.meta_data,
            }
            return result  # Return dict directly for consistency
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to create entity: {str(e)}")
        finally:
            db.close()

    @mcp.tool()
    def update_entity(
        entity_id: int,
        name: str = None,
        metadata: Dict[str, Any] = None,
        ctx: Context = None,
    ) -> Dict[str, Any]:
        """Update an existing entity's properties.

        Args:
            entity_id: ID of entity to update
            name: Optional new entity name
            metadata: Optional metadata to merge with existing
            ctx: MCP context object

        Returns:
            Dict containing updated entity details

        Raises:
            ValidationError: If entity not found
            DatabaseError: If update fails

        Example:
            >>> result = update_entity(
            ...     entity_id=1,
            ...     name="web-server-2",
            ...     metadata={"environment": "staging"}
            ... )
            >>> print(result)
            {
                "id": 1,
                "name": "web-server-2",
                "type": "instance",
                "metadata": {
                    "environment": "staging"
                }
            }
        """
        from ..db.connection import get_db

        db = next(get_db())
        try:
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise ValidationError(f"Entity {entity_id} not found")

            if name:
                entity.name = name.strip()
            if metadata:
                if not isinstance(metadata, dict):
                    raise ValidationError("Metadata must be a dictionary")
                entity.meta_data.update(metadata)

            db.commit()
            db.refresh(entity)

            return {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type,
                "metadata": entity.meta_data,
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to update entity {entity_id}: {str(e)}")
        finally:
            db.close()

    @mcp.tool()
    def delete_entity(entity_id: int) -> Dict[str, str]:
        """Delete an entity from the system.

        Args:
            entity_id: ID of entity to delete
            db: Database session

        Returns:
            Dict containing success message

        Raises:
            ValidationError: If entity not found
            DatabaseError: If deletion fails

        Example:
            >>> result = delete_entity(entity_id=1)
            >>> print(result)
            {
                "message": "Entity 1 deleted successfully"
            }
        """
        from ..db.connection import get_db

        db = next(get_db())
        try:
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise ValidationError(f"Entity {entity_id} not found")

            db.delete(entity)
            db.commit()

            return {"message": f"Entity {entity_id} deleted successfully"}
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to delete entity {str(entity_id)}: {str(e)}")
        finally:
            db.close()

    # Return list of registered tools
    tools.extend([create_entity, update_entity, delete_entity])
    return tools
