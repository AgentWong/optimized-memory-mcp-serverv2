"""Provider Resources model for infrastructure providers."""

from sqlalchemy import Column, JSON, String
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, TimestampMixin
from .arguments import ResourceArgument


class Provider(Base, BaseModel, TimestampMixin):
    """Represents an infrastructure provider and its resources.

    Stores information about cloud/infrastructure providers
    and their available resource types.
    """

    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # e.g. 'aws', 'azure', 'gcp'
    version = Column(String, nullable=False)
    meta_data = Column(JSON, nullable=False, default=dict)
    # Relationships
    resources = relationship(
        ResourceArgument, back_populates="provider", cascade="all, delete-orphan"
    )
