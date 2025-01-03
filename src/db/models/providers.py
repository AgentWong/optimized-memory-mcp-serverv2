"""
Provider Resources model for infrastructure providers.
"""
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin

class Provider(BaseModel, TimestampMixin):
    """
    Represents an infrastructure provider and its resources.
    
    Stores information about cloud/infrastructure providers
    and their available resource types.
    """
    
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # e.g. 'aws', 'azure', 'gcp'
    version = Column(String, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)
    
    # Relationships
    resources = relationship("ResourceArgument", 
                           back_populates="provider",
                           cascade="all, delete-orphan")
