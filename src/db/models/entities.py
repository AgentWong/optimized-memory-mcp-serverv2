"""
Entity model for storing core objects.
"""
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin

class Entity(BaseModel, TimestampMixin):
    """
    Represents a core entity in the system.
    
    Entities are the primary objects that can have relationships
    and observations attached to them.
    """
    
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    # Composite index for name+type lookups
    __table_args__ = (
        sa.Index('ix_entity_name_type', 'name', 'type'),
    )
    metadata = Column(JSON, nullable=False, default=dict)
    
    # Relationships
    relationships = relationship("Relationship", 
                               back_populates="entity",
                               cascade="all, delete-orphan")
    observations = relationship("Observation",
                              back_populates="entity",
                              cascade="all, delete-orphan")
