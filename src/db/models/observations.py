"""Observation model for storing entity attributes."""

from sqlalchemy import Column, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin


class Observation(BaseModel, TimestampMixin):
    """Represents an observation about an entity.

    Stores attributes, measurements, or other observations
    about entities with timestamps and metadata.
    """

    entity_id = Column(Integer, ForeignKey("entity.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    # Composite indexes for common lookups
    __table_args__ = (
        Index("ix_observation_entity_type", "entity_id", "type"),
        Index("ix_observation_created_entity", "created_at", "entity_id"),
        Index("ix_observation_type_value", "type", "value"),
    )
    value = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)

    # Relationships
    entity = relationship("Entity", back_populates="observations")
