"""Ansible Collections model for automation resources."""

from sqlalchemy import Column, JSON, String
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, TimestampMixin


class AnsibleCollection(Base, BaseModel, TimestampMixin):
    """Represents an Ansible collection and its modules.

    Stores information about Ansible collections including
    their modules and requirements.
    """

    namespace = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    version = Column(String, nullable=False)
    meta_data = Column(JSON, nullable=False, default=dict)
    # Relationships
    modules = relationship(
        "ModuleParameter", back_populates="collection", cascade="all, delete-orphan"
    )
