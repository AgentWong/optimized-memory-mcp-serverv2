"""Base model utilities and mixins."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, MetaData
from sqlalchemy.ext.declarative import declared_attr

from ..init_db import Base

# Create a custom MetaData instance
metadata = MetaData()

class TimestampMixin:
    """Mixin to add created/updated timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class BaseModel(Base):
    """Abstract base model with common fields and methods."""

    __abstract__ = True
    metadata = metadata  # Use custom metadata instance

    id = Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
