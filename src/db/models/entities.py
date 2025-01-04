"""Entity model for storing core objects."""

from sqlalchemy import Column, Index, JSON, String
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, TimestampMixin


class Entity(Base, BaseModel, TimestampMixin):
    """Represents a core entity in the system.

    Entities are the primary objects that can have relationships
    and observations attached to them.
    """

    name = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    # Composite indexes for common lookups  
    __table_args__ = (
        Index("ix_entity_name_type", "name", "entity_type"),
        Index("ix_entity_created_type", "created_at", "entity_type"),
        Index("ix_entity_updated_type", "updated_at", "entity_type"),
    )
    meta_data = Column(JSON, nullable=False, default=dict)
    tags = Column(JSON, nullable=False, default=list)

    # Relationships
    relationships = relationship(
        "Relationship",
        back_populates="entity",
        cascade="all, delete-orphan",
        foreign_keys="[Relationship.entity_id]",
    )
    observations = relationship(
        "Observation", back_populates="entity", cascade="all, delete-orphan"
    )
