"""Initial schema for MCP Server database.

This migration creates the core database schema including tables for:
- Entities: Base objects in the system
- Relationships: Connections between entities
- Observations: Data points about entities
- Providers: Infrastructure providers
- Resource Arguments: Provider resource parameters
- Ansible Collections: Ansible Galaxy collections
- Module Parameters: Ansible module parameters

Each table includes created_at/updated_at timestamps and appropriate indexes
for optimal query performance.

Revision ID: initial_schema
Create Date: 2025-01-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision: str = "initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Entity table
    op.create_table(
        "entity",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("metadata", sqlite.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_entity_name", "entity", ["name"])
    op.create_index("ix_entity_type", "entity", ["type"])

    # Relationship table
    op.create_table(
        "relationship",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("metadata", sqlite.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["target_id"], ["entity.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_relationship_type", "relationship", ["type"])

    # Observation table
    op.create_table(
        "observation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("value", sqlite.JSON(), nullable=False),
        sa.Column("metadata", sqlite.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_observation_type", "observation", ["type"])

    # Provider table
    op.create_table(
        "provider",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("metadata", sqlite.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_provider_name", "provider", ["name"])
    op.create_index("ix_provider_type", "provider", ["type"])

    # Resource Argument table
    op.create_table(
        "resourceargument",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("resource_type", sa.String(), nullable=False),
        sa.Column("schema", sqlite.JSON(), nullable=False),
        sa.Column("metadata", sqlite.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["provider.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resourceargument_name", "resourceargument", ["name"])
    op.create_index(
        "ix_resourceargument_resource_type", "resourceargument", ["resource_type"]
    )

    # Ansible Collection table
    op.create_table(
        "ansiblecollection",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("namespace", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("metadata", sqlite.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ansiblecollection_namespace", "ansiblecollection", ["namespace"]
    )
    op.create_index("ix_ansiblecollection_name", "ansiblecollection", ["name"])

    # Module Parameter table
    op.create_table(
        "moduleparameter",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("module_name", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("schema", sqlite.JSON(), nullable=False),
        sa.Column("metadata", sqlite.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["ansiblecollection.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_moduleparameter_module_name", "moduleparameter", ["module_name"]
    )
    op.create_index("ix_moduleparameter_name", "moduleparameter", ["name"])


def downgrade() -> None:
    op.drop_table("moduleparameter")
    op.drop_table("ansiblecollection")
    op.drop_table("resourceargument")
    op.drop_table("provider")
    op.drop_table("observation")
    op.drop_table("relationship")
    op.drop_table("entity")
