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
        if "type" not in kwargs:
            kwargs["type"] = "depends_on"  # Default type
        if "entity_id" not in kwargs and "source_id" in kwargs:
            kwargs["entity_id"] = kwargs["source_id"]

        # Initialize base class
        super().__init__(**kwargs)

        # Validate relationship type
        if self.type not in self.VALID_TYPES:
            raise ValueError(f"Invalid relationship type: {self.type}")
        if not self.relationship_type or not self.relationship_type.strip():
            raise ValueError("Relationship type cannot be empty")
        if self.source_id == self.target_id:
            raise ValueError("Source and target cannot be the same entity")

        # Validate entity references
        from sqlalchemy import inspect
        if inspect(self).session:
            session = inspect(self).session
            from .entities import Entity
            for field, value in [('entity_id', self.entity_id),
                               ('source_id', self.source_id),
                               ('target_id', self.target_id)]:
                if not session.query(Entity).filter_by(id=value).first():
                    from sqlalchemy.exc import IntegrityError
                    raise IntegrityError(
                        f"Referenced entity {field} does not exist",
                        params={field: value},
                        orig=None
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
