"""Observation model for storing entity attributes."""

from sqlalchemy import Column, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, TimestampMixin


class Observation(Base, BaseModel, TimestampMixin):
    """Represents an observation about an entity.

    Stores attributes, measurements, or other observations
    about entities with timestamps and metadata.
    """

    entity_id = Column(Integer, ForeignKey("entity.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # Observation type
    observation_type = Column(
        String, nullable=False, index=True
    )  # Specific observation kind

    VALID_TYPES = {
        "state",
        "metric",
        "event",
        "configuration",
        "dependency",
        "security",
        "performance",
        "test"  # Added for testing purposes
    }

    def __init__(self, **kwargs):
        """Initialize an Observation with validation."""
        if "data" in kwargs:
            kwargs["value"] = kwargs.pop("data")
        if "type" not in kwargs:
            kwargs["type"] = "state"  # Default type
        if "observation_type" not in kwargs:
            kwargs["observation_type"] = "default"  # Default observation type
        super().__init__(**kwargs)
        if self.type not in self.VALID_TYPES:
            raise ValueError(f"Invalid observation type: {self.type}")
        if not self.observation_type or not self.observation_type.strip():
            raise ValueError("Observation type cannot be empty")
        if not isinstance(self.value, (dict, list)):
            raise ValueError("Value must be a JSON-serializable object")

    # Composite indexes for common lookups
    __table_args__ = (
        Index("ix_observation_entity_type", "entity_id", "type"),
        Index("ix_observation_created_entity", "created_at", "entity_id"),
        Index("ix_observation_type_value", "type", "value"),
    )
    value = Column(JSON, nullable=False)
    meta_data = Column(JSON, nullable=False, default=dict)

    # Relationships
    entity = relationship("Entity", back_populates="observations")
