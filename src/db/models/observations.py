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
        "test",  # Added for testing purposes
    }

    def __init__(self, **kwargs):
        """Initialize an Observation with validation."""
        from sqlalchemy.exc import IntegrityError

        # Validate required fields and types before calling super()
        required_fields = ["entity_id", "observation_type", "type", "value"]
        for field in required_fields:
            if field not in kwargs or kwargs[field] is None:
                raise IntegrityError(
                    f"{field} is required", params={field: None}, orig=None
                )

        # Validate entity_id
        entity_id = kwargs.get("entity_id")
        if entity_id is None:
            from sqlalchemy.exc import IntegrityError

            raise IntegrityError(
                "INSERT INTO observations (entity_id) VALUES (NULL)",
                None,
                Exception("entity_id cannot be null"),
                orig=Exception("NOT NULL constraint failed: observations.entity_id"),
            )

        if not isinstance(entity_id, int):
            from sqlalchemy.exc import IntegrityError

            raise IntegrityError(
                "INSERT INTO observations (entity_id) VALUES (?)",
                [entity_id],
                Exception("entity_id must be an integer"),
                orig=Exception("CHECK constraint failed: entity_id type"),
            )

        if entity_id <= 0:
            from sqlalchemy.exc import IntegrityError

            raise IntegrityError(
                "INSERT INTO observations (entity_id) VALUES (?)",
                [entity_id],
                Exception("entity_id must be a positive integer"),
                orig=Exception("CHECK constraint failed: entity_id > 0"),
            )

        # Entity validation will be handled by foreign key constraint

        # Validate type
        obs_type = kwargs.get("type")
        if not obs_type or obs_type not in self.VALID_TYPES:
            raise IntegrityError(
                f"Invalid observation type: {obs_type}",
                params={"type": obs_type},
                orig=None,
            )

        # Validate observation_type
        obs_subtype = kwargs.get("observation_type")
        if not obs_subtype or not isinstance(obs_subtype, str):
            raise IntegrityError(
                "observation_type must be a non-empty string",
                params={"observation_type": obs_subtype},
                orig=None,
            )

        # Validate value
        value = kwargs.get("value")
        if not isinstance(value, (dict, list)):
            raise IntegrityError(
                "value must be a dict or list", params={"value": value}, orig=None
            )

        # Initialize base class to get session
        super().__init__(**kwargs)

        # Always validate entity_id type and value
        if not isinstance(self.entity_id, int) or self.entity_id <= 0:
            from sqlalchemy.exc import IntegrityError

            raise IntegrityError(
                "INSERT INTO observations (entity_id) VALUES (?)",
                [self.entity_id],
                Exception("entity_id must be a positive integer"),
                orig=Exception("CHECK constraint failed: entity_id > 0"),
            )

        # Always validate entity exists
        from sqlalchemy import inspect

        if inspect(self).session:
            session = inspect(self).session
            from .entities import Entity

            # Check if entity exists
            entity = session.query(Entity).get(self.entity_id)
            if not entity:
                from sqlalchemy.exc import IntegrityError

                raise IntegrityError(
                    "INSERT INTO observations (entity_id) VALUES (?)",
                    [self.entity_id],
                    Exception(f"Referenced entity_id={self.entity_id} does not exist"),
                    orig=Exception(
                        "FOREIGN KEY constraint failed: observations.entity_id"
                    ),
                )

            try:
                # Force foreign key check and validation
                session.flush([self])
                session.refresh(self)
                if not self.entity:
                    raise IntegrityError(
                        "INSERT INTO observations (entity_id) VALUES (?)",
                        [self.entity_id],
                        Exception("Failed to validate entity relationship"),
                        orig=Exception(
                            "FOREIGN KEY constraint failed: observations.entity_id"
                        ),
                    )
            except Exception as e:
                session.rollback()
                raise IntegrityError(
                    "Failed to validate observation",
                    params={"entity_id": self.entity_id},
                    orig=e,
                )

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
