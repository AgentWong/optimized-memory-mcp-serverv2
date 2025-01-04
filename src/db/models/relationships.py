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
    target_id = Column(Integer, ForeignKey("entity.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
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
