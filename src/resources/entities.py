"""Entity-related MCP resources."""

# Standard library imports
from datetime import datetime
from typing import List, Dict, Any, Set
from uuid import UUID

# Third-party imports
from mcp.server.fastmcp import FastMCP, Context
from sqlalchemy.orm import joinedload

# Local imports
from ..db.connection import get_db
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError, ValidationError
from ..utils.cache import generate_cache_key, get_cached, set_cached

VALID_ENTITY_TYPES: Set[str] = {"provider", "module", "resource"}


def register_resources(mcp: FastMCP) -> None:
    """Register entity-related resources with the MCP server.

    Args:
        mcp: The FastMCP server instance to register resources with
    """

    @mcp.resource(
        "entities://list?page={page}&per_page={per_page}&type={type}&created_after={created_after}&ctx={ctx}"
    )
    def list_entities(
        ctx: Context,
        page: str = "null",
        per_page: str = "null",
        type: str = "null",
        created_after: str = "null",
    ) -> Dict[str, Any]:
        """List entities with pagination and filtering.

        Args:
            ctx: MCP context object
            page: Page number (default: 1)
            per_page: Items per page (default: 50, max: 100)
            type: Filter by entity type
            created_after: Filter by creation date (ISO format)

        Returns:
            Dict containing:
                - items: List of entity dictionaries
                - total: Total number of matching entities
                - page: Current page number
                - pages: Total number of pages

        Raises:
            DatabaseError: If database query fails
            ValidationError: If invalid parameters provided
        """

        # Convert and validate pagination params
        try:
            page_num = int(page) if page != "null" else 1
            items_per_page = int(per_page) if per_page != "null" else 50
            if items_per_page < 1 or items_per_page > 100:
                raise ValueError("per_page must be between 1 and 100")
            if page_num < 1:
                raise ValueError("page must be positive")
        except ValueError as e:
            raise ValidationError(f"Invalid pagination parameters: {str(e)}")

        # Handle optional parameters
        entity_type = None if type == "null" else type
        created_after_date = None

        # Parse created_after if provided and not null
        if created_after and created_after != "null":
            try:
                created_after_date = datetime.fromisoformat(created_after)
            except ValueError:
                raise ValidationError("created_after must be ISO format datetime")

        db = next(get_db())
        try:
            # Generate cache key for this query
            cache_params = {"page": page, "per_page": per_page}
            if type:
                cache_params["type"] = type
            if created_after:
                cache_params["created_after"] = created_after

            cache_key = generate_cache_key("entity_list", "all", **cache_params)

            # Check cache
            cached_result = get_cached(cache_key)
            if cached_result:
                ctx.info(
                    "Retrieved entity list from cache",
                    details={"cache_key": cache_key, "params": cache_params},
                )
                return cached_result

            # Build query with filters
            query = db.query(Entity)

            if entity_type:
                # Validate entity type
                if entity_type not in VALID_ENTITY_TYPES:
                    raise ValidationError(
                        f"Invalid entity type: {entity_type}",
                        details={"valid_types": list(VALID_ENTITY_TYPES)},
                    )
                query = query.filter(Entity.entity_type == entity_type)
            if created_after:
                query = query.filter(Entity.created_at >= created_after_date)

            # Get total count
            total = query.count()

            # Apply pagination
            offset = (page_num - 1) * items_per_page
            entities = query.offset(offset).limit(items_per_page).all()

            # Calculate total pages
            total_pages = (total + items_per_page - 1) // items_per_page

            # Log via MCP context with query details
            ctx.info(
                f"Listed {len(entities)} entities (page {page}/{total_pages})",
                details={
                    "type_filter": type,
                    "created_after": created_after,
                    "total_results": total,
                    "page_size": per_page,
                },
            )

            result = {
                "items": [entity.to_dict() for entity in entities],
                "total": total,
                "page": page,
                "pages": total_pages,
            }

            # Cache the results
            set_cached(cache_key, result)

            return result
        except ValidationError:
            raise
        except Exception as e:
            ctx.error(f"Database error while listing entities: {str(e)}")
            raise DatabaseError(
                "Failed to list entities",
                details={
                    "error": str(e),
                    "filters": {"type": type, "created_after": created_after},
                },
            )

    @mcp.resource("entities://{id}?include={include}&ctx={ctx}")
    def get_entity(
        ctx: Context, id: str, include: str = "null"
    ) -> Dict[str, Any]:
        """Get details for a specific entity with optional related data.

        Args:
            ctx: MCP context object
            id: Unique identifier of the entity
            include: Comma-separated list of related data to include
                    (relationships, observations)

        Returns:
            Dict containing entity details and optionally related data

        Raises:
            DatabaseError: If entity not found or database error occurs
            ValidationError: If id format is invalid or unknown include option
        """
        from ..utils.errors import ValidationError
        from sqlalchemy.orm import joinedload

        # Validate id format
        from uuid import UUID

        try:
            entity_uuid = UUID(id)
        except ValueError as e:
            raise ValidationError(
                "Invalid id format - must be UUID",
                details={"id": id, "error": str(e)},
            )

        # Parse and validate include parameter
        include_options = set()
        if include:
            valid_options = {"relationships", "observations"}
            for option in include.split(","):
                option = option.strip()
                if option not in valid_options:
                    raise ValidationError(
                        f"Invalid include option: {option}",
                        details={"valid_options": list(valid_options)},
                    )
                include_options.add(option)

        # Check cache first
        cache_key = generate_cache_key("entity", id, include=include)
        cached_result = get_cached(cache_key)
        if cached_result:
            ctx.info(f"Retrieved entity {id} from cache")
            return cached_result

        # Get database session
        db = next(get_db())

        try:
            # Build query with optional joins
            query = db.query(Entity)

            if "relationships" in include_options:
                query = query.options(joinedload(Entity.relationships))
            if "observations" in include_options:
                query = query.options(joinedload(Entity.observations))

            # Execute query
            entity = query.filter(Entity.id == str(entity_uuid)).first()

            if not entity:
                raise DatabaseError(f"Entity {id} not found", details={"id": id})

            # Convert to dict with related data and counts
            result = entity.to_dict()

            # Add relationship/observation counts
            result["relationship_count"] = len(entity.relationships)
            result["observation_count"] = len(entity.observations)

            # Log access via MCP context with details
            ctx.info(
                f"Retrieved entity {id}",
                details={
                    "type": entity.entity_type,
                    "included_data": list(include_options) if include_options else None,
                },
            )

            # Cache the result
            set_cached(cache_key, result)
            return result

        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get entity {id}", details={"error": str(e)})
