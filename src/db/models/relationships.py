"""Relationship model for connecting entities."""

from sqlalchemy import Column, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, TimestampMixin


class Relationship(Base, BaseModel, TimestampMixin):
    """Represents a relationship between entities.

    Captures directed relationships between entities with
    optional metadata and relationship type.
    """

    entity_id = Column(Integer, ForeignKey("entity.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("entity.id"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("entity.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # Entity relationship category
    relationship_type = Column(
        String, nullable=False, index=True
    )  # Specific relationship kind

    VALID_TYPES = {
        "depends_on",
        "contains",
        "references",
        "manages",
        "configures",
        "monitors",
        "deploys",
    }

    def __init__(self, **kwargs):
        """Initialize a Relationship with validation."""
        # Set default entity_id if not provided
        if "entity_id" not in kwargs:
            kwargs["entity_id"] = kwargs.get("source_id")

        # Set default type if not provided
        if "type" not in kwargs and "relationship_type" in kwargs:
            kwargs["type"] = kwargs["relationship_type"]

        # Validate required fields
        required_fields = [
            "source_id",
            "target_id",
            "type",
            "relationship_type",
            "entity_id",
        ]
        for field in required_fields:
            if field not in kwargs or kwargs[field] is None:
                from sqlalchemy.exc import IntegrityError

                raise IntegrityError(
                    f"{field} is required", params={field: None}, orig=None
                )

        # Initialize base class first to get session
        super().__init__(**kwargs)

        # Validate entity references exist
        from sqlalchemy import inspect

        if inspect(self).session:
            session = inspect(self).session
            from .entities import Entity

            for field, value in [
                ("entity_id", self.entity_id),
                ("source_id", self.source_id),
                ("target_id", self.target_id),
            ]:
                if not session.query(Entity).get(value):
                    raise IntegrityError(
                        f"Referenced entity {field}={value} does not exist",
                        params={field: value},
                        orig=None,
                    )

        # Initialize base class
        super().__init__(**kwargs)

        # Validate entity references
        from sqlalchemy import inspect

        if inspect(self).session:
            session = inspect(self).session
            from .entities import Entity

            for field, value in [
                ("entity_id", self.entity_id),
                ("source_id", self.source_id),
                ("target_id", self.target_id),
            ]:
                if not session.query(Entity).filter_by(id=value).first():
                    from sqlalchemy.exc import IntegrityError

                    raise IntegrityError(
                        f"Referenced entity {field} does not exist",
                        params={field: value},
                        orig=None,
                    )

    # Composite indexes for common lookups and traversals
    __table_args__ = (
        Index("ix_relationship_entity_type", "entity_id", "type"),
        Index("ix_relationship_target_type", "target_id", "type"),
        Index("ix_relationship_type_entities", "type", "entity_id", "target_id"),
        Index("ix_relationship_created_type", "created_at", "type"),
    )
    meta_data = Column(JSON, nullable=False, default=dict)

    # Relationships
    entity = relationship(
        "Entity",
        back_populates="relationships",
        foreign_keys="[Relationship.entity_id]",
    )
    target = relationship("Entity", foreign_keys="[Relationship.target_id]")
