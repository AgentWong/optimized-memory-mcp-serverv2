"""Module Parameters model for Ansible module configuration."""

from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, TimestampMixin


class ModuleParameter(Base, BaseModel, TimestampMixin):
    """Represents parameters for Ansible modules.

    Stores configuration parameters and validation rules
    for Ansible module arguments.
    """

    collection_id = Column(Integer, ForeignKey("ansiblecollection.id"), nullable=False)
    module_name = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    schema = Column(JSON, nullable=False)  # JSON Schema for validation
    module_metadata = Column(JSON, nullable=False, default=dict)

    # Relationships
    collection = relationship("AnsibleCollection", back_populates="modules")
