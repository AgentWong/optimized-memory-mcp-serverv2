"""
Relationship model for connecting entities.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin

class Relationship(BaseModel, TimestampMixin):
    """
    Represents a relationship between entities.
    
    Captures directed relationships between entities with
    optional metadata and relationship type.
    """
    
    entity_id = Column(Integer, ForeignKey('entity.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('entity.id'), nullable=False)
    type = Column(String, nullable=False, index=True)
    metadata = Column(JSON, nullable=False, default=dict)
    
    # Relationships
    entity = relationship("Entity", back_populates="relationships",
                         foreign_keys=[entity_id])
    target = relationship("Entity", foreign_keys=[target_id])
