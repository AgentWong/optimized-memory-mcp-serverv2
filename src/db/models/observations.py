"""
Observation model for storing entity attributes.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin

class Observation(BaseModel, TimestampMixin):
    """
    Represents an observation about an entity.
    
    Stores attributes, measurements, or other observations
    about entities with timestamps and metadata.
    """
    
    entity_id = Column(Integer, ForeignKey('entity.id'), nullable=False)
    type = Column(String, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)
    
    # Relationships
    entity = relationship("Entity", back_populates="observations")
