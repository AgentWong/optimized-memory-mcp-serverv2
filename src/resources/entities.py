"""Entity-related MCP resources."""
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from ..db.connection import get_db
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError
from ..utils.cache import generate_cache_key, get_cached, set_cached

def register_resources(mcp: FastMCP) -> None:
    """Register entity-related MCP resources."""

    @mcp.resource("entities://list{?page,per_page,type,created_after}")
    async def list_entities(
        ctx: Context,
        page: int = 1,
        per_page: int = 50,
        type: str = None,
        created_after: str = None
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
        from ..utils.errors import ValidationError
        from datetime import datetime
        
        # Validate pagination params
        try:
            page = int(page)
            per_page = int(per_page)
            if per_page < 1 or per_page > 100:
                raise ValueError("per_page must be between 1 and 100")
            if page < 1:
                raise ValueError("page must be positive")
        except ValueError as e:
            raise ValidationError(f"Invalid pagination parameters: {str(e)}")

        # Parse created_after if provided
        if created_after:
            try:
                created_after_date = datetime.fromisoformat(created_after)
            except ValueError:
                raise ValidationError("created_after must be ISO format datetime")

        db = next(get_db())
        try:
            # Generate cache key for this query
            cache_params = {
                "page": page,
                "per_page": per_page
            }
            if type:
                cache_params["type"] = type
            if created_after:
                cache_params["created_after"] = created_after

            cache_key = generate_cache_key("entity_list", "all", **cache_params)
        
            # Check cache
            cached_result = get_cached(cache_key)
            if cached_result:
                await ctx.info("Retrieved entity list from cache", 
                             details={"cache_key": cache_key, "params": cache_params})
                return cached_result

            # Build query with filters
            query = db.query(Entity)
            
            if type:
                # Validate entity type
                valid_types = {"provider", "module", "resource"}
                if type not in valid_types:
                    raise ValidationError(
                        f"Invalid entity type: {type}",
                        details={"valid_types": list(valid_types)}
                    )
                query = query.filter(Entity.type == type)
            if created_after:
                query = query.filter(Entity.created_at >= created_after_date)

            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            entities = query.offset(offset).limit(per_page).all()
            
            # Calculate total pages
            total_pages = (total + per_page - 1) // per_page

            # Log via MCP context with query details
            await ctx.info(
                f"Listed {len(entities)} entities (page {page}/{total_pages})",
                details={
                    "type_filter": type,
                    "created_after": created_after,
                    "total_results": total,
                    "page_size": per_page
                }
            )
            
            result = {
                "items": [entity.to_dict() for entity in entities],
                "total": total,
                "page": page,
                "pages": total_pages
            }
            
            # Cache the results
            set_cached(cache_key, result)
            
            return result
        except ValidationError:
            raise
        except Exception as e:
            await ctx.error(f"Database error while listing entities: {str(e)}")
            raise DatabaseError(
                "Failed to list entities",
                details={"error": str(e), "filters": {"type": type, "created_after": created_after}}
            )

    @mcp.resource("entities://{entity_id}{?include}")
    async def get_entity(
        ctx: Context,
        entity_id: str,
        include: str = None
    ) -> Dict[str, Any]:
        """Get details for a specific entity with optional related data.
        
        Args:
            ctx: MCP context object
            entity_id: Unique identifier of the entity
            include: Comma-separated list of related data to include
                    (relationships, observations)
            
        Returns:
            Dict containing entity details and optionally related data
            
        Raises:
            DatabaseError: If entity not found or database error occurs
            ValidationError: If entity_id format is invalid or unknown include option
        """
        from ..utils.errors import ValidationError
        from sqlalchemy.orm import joinedload
        
        # Validate entity_id format
        from uuid import UUID
        try:
            entity_uuid = UUID(entity_id)
        except ValueError as e:
            raise ValidationError(
                "Invalid entity ID format - must be UUID",
                details={"entity_id": entity_id, "error": str(e)}
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
                        details={"valid_options": list(valid_options)}
                    )
                include_options.add(option)

        # Check cache first
        cache_key = generate_cache_key("entity", entity_id, include=include)
        cached_result = get_cached(cache_key)
        if cached_result:
            await ctx.info(f"Retrieved entity {entity_id} from cache")
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
            entity = query.filter(Entity.id == entity_uuid).first()
            
            if not entity:
                raise DatabaseError(
                    f"Entity {entity_id} not found",
                    details={"entity_id": entity_id}
                )

            # Convert to dict with related data and counts
            result = entity.to_dict()
            
            # Add relationship/observation counts
            result["relationship_count"] = db.query(Entity.relationships).filter(Entity.id == entity_uuid).count()
            result["observation_count"] = db.query(Entity.observations).filter(Entity.id == entity_uuid).count()
            
            # Log access via MCP context with details
            await ctx.info(
                f"Retrieved entity {entity_id}",
                details={
                    "type": entity.type,
                    "included_data": list(include_options) if include_options else None
                }
            )
            
            # Cache the result
            set_cached(cache_key, result)
            return result

        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                f"Failed to get entity {entity_id}",
                details={"error": str(e)}
            )
