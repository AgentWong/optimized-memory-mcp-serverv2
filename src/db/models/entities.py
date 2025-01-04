"""Entity model for storing core objects."""
from sqlalchemy import Column, Index, JSON, String
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin


class Entity(BaseModel, TimestampMixin):
    """Represents a core entity in the system.

    Entities are the primary objects that can have relationships
    and observations attached to them.
    """

    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    # Composite indexes for common lookups
    __table_args__ = (
        Index('ix_entity_name_type', 'name', 'type'),
        Index('ix_entity_created_type', 'created_at', 'type'),
        Index('ix_entity_updated_type', 'updated_at', 'type')
    )
    metadata = Column(JSON, nullable=False, default=dict)

    # Relationships
    relationships = relationship(
        "Relationship",
        back_populates="entity",
        cascade="all, delete-orphan"
    )
    observations = relationship(
        "Observation",
        back_populates="entity",
        cascade="all, delete-orphan"
    )
