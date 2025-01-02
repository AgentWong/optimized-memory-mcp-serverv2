# Database Schema Documentation

## Overview
This document describes the database schema for the MCP Server. The schema is implemented using SQLAlchemy models and consists of several core tables for managing entities, relationships, observations, and infrastructure-as-code (IaC) resources.

## Core Tables

### Entity
The central table for storing core objects in the system.

**Table: entity**
- `id` (Integer, Primary Key): Unique identifier
- `name` (String, Indexed): Entity name
- `type` (String, Indexed): Entity type
- `metadata` (JSON): Additional metadata
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

### Relationship
Stores directed relationships between entities.

**Table: relationship**
- `id` (Integer, Primary Key): Unique identifier
- `entity_id` (Integer, Foreign Key): Source entity ID
- `target_id` (Integer, Foreign Key): Target entity ID
- `type` (String, Indexed): Relationship type
- `metadata` (JSON): Additional metadata
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

### Observation
Stores attributes and measurements about entities.

**Table: observation**
- `id` (Integer, Primary Key): Unique identifier
- `entity_id` (Integer, Foreign Key): Related entity ID
- `type` (String, Indexed): Observation type
- `value` (JSON): Observation value
- `metadata` (JSON): Additional metadata
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

## Infrastructure-as-Code Tables

### Provider
Stores information about infrastructure providers.

**Table: provider**
- `id` (Integer, Primary Key): Unique identifier
- `name` (String, Indexed): Provider name
- `type` (String, Indexed): Provider type (e.g., aws, azure, gcp)
- `version` (String): Provider version
- `metadata` (JSON): Additional metadata
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

### ResourceArgument
Stores configuration parameters for provider resources.

**Table: resourceargument**
- `id` (Integer, Primary Key): Unique identifier
- `provider_id` (Integer, Foreign Key): Related provider ID
- `name` (String, Indexed): Argument name
- `resource_type` (String, Indexed): Type of resource
- `schema` (JSON): JSON Schema for validation
- `metadata` (JSON): Additional metadata
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

### AnsibleCollection
Stores information about Ansible collections.

**Table: ansiblecollection**
- `id` (Integer, Primary Key): Unique identifier
- `namespace` (String, Indexed): Collection namespace
- `name` (String, Indexed): Collection name
- `version` (String): Collection version
- `metadata` (JSON): Additional metadata
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

### ModuleParameter
Stores configuration parameters for Ansible modules.

**Table: moduleparameter**
- `id` (Integer, Primary Key): Unique identifier
- `collection_id` (Integer, Foreign Key): Related collection ID
- `module_name` (String, Indexed): Module name
- `name` (String, Indexed): Parameter name
- `schema` (JSON): JSON Schema for validation
- `metadata` (JSON): Additional metadata
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

## Relationships Between Tables

### Core Relationships
- Entity -> Relationship (One-to-Many)
- Entity -> Observation (One-to-Many)
- Relationship -> Entity (Many-to-One) [both source and target]

### IaC Relationships
- Provider -> ResourceArgument (One-to-Many)
- AnsibleCollection -> ModuleParameter (One-to-Many)

## Indexes
The schema includes indexes on frequently queried columns:
- Entity: name, type
- Relationship: type
- Observation: type
- Provider: name, type
- ResourceArgument: name, resource_type
- AnsibleCollection: namespace, name
- ModuleParameter: module_name, name

## Common Fields
All tables include:
- Primary key `id`
- Timestamps `created_at` and `updated_at`
- JSON `metadata` field for extensibility

## Schema Migrations
Database migrations are managed using Alembic. See the `migrations/` directory for version history and change details.
