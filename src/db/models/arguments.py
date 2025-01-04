"""Resource Arguments model for provider resource parameters."""

from sqlalchemy import Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, TimestampMixin


class ResourceArgument(Base, BaseModel, TimestampMixin):
    """Represents arguments/parameters for provider resources.

    Stores configuration parameters and validation rules
    for infrastructure resource types.
    """

    provider_id = Column(Integer, ForeignKey("provider.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False, index=True)
    schema = Column(JSON, nullable=False)  # JSON Schema for validation
    resource_metadata = Column(JSON, nullable=False, default=dict)
    # Relationships
    provider = relationship("Provider", back_populates="resources")
