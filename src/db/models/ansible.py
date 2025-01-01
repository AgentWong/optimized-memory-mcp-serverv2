"""
Ansible Collections model for automation resources.
"""
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin

class AnsibleCollection(BaseModel, TimestampMixin):
    """
    Represents an Ansible collection and its modules.
    
    Stores information about Ansible collections including
    their modules and requirements.
    """
    
    namespace = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    version = Column(String, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)
    
    # Relationships
    modules = relationship("ModuleParameter",
                         back_populates="collection",
                         cascade="all, delete-orphan")
