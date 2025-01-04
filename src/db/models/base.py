"""Base model utilities and mixins."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base class for all models."""

    # Configure class-wide metadata
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class TimestampMixin:
    """Mixin to add created/updated timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class BaseModel:
    """Abstract base model with common fields and methods."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __init__(self, **kwargs):
        """Initialize model with provided attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
