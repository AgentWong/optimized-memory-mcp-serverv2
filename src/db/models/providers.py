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
    namespace = Column(
        String, nullable=True, index=True
    )  # Organization/project namespace
    type = Column(String, nullable=False, index=True)  # e.g. 'aws', 'azure', 'gcp'

    def __init__(self, **kwargs):
        """Initialize a Provider with validation."""
        super().__init__(**kwargs)
        if self.type not in ("aws", "azure", "gcp", "kubernetes", "terraform"):
            raise ValueError(f"Invalid provider type: {self.type}")
        if self.namespace and not self.namespace.strip():
            raise ValueError("Namespace cannot be empty string if provided")

    version = Column(String, nullable=False)
    meta_data = Column(JSON, nullable=False, default=dict)
    # Relationships
    resources = relationship(
        ResourceArgument, back_populates="provider", cascade="all, delete-orphan"
    )
