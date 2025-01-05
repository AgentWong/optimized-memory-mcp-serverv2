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
        # Validate entity_id before calling super()
        if "entity_id" not in kwargs or not kwargs["entity_id"]:
            from sqlalchemy.exc import IntegrityError
            raise IntegrityError(
                "entity_id is required",
                params={"entity_id": None},
                orig=None
            )

        # Validate observation_type
        if "observation_type" not in kwargs or not kwargs.get("observation_type"):
            from sqlalchemy.exc import IntegrityError
            raise IntegrityError(
                "observation_type is required",
                params={"observation_type": None},
                orig=None
            )

        # Initialize base class to get session
        super().__init__(**kwargs)

        # Validate entity exists
        from sqlalchemy import inspect
        if inspect(self).session:
            session = inspect(self).session
            from .entities import Entity
            entity = session.query(Entity).get(self.entity_id)
            if not entity:
                from sqlalchemy.exc import IntegrityError
                raise IntegrityError(
                    f"Referenced entity_id={self.entity_id} does not exist",
                    params={"entity_id": self.entity_id},
                    orig=None
                )

        if not self.type or self.type not in self.VALID_TYPES:
            raise ValueError(f"Invalid observation type: {self.type}")

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
