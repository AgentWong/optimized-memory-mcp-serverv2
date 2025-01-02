# Enhanced MCP Server Implementation Tasks

## Initial Setup

1. Environment & Database Setup
```python
from mcp.server.fastmcp import FastMCP
import os
import sqlite3

mcp = FastMCP("IaC Memory Server",
              dependencies=["sqlite3", "uuid"])

# Database connection handling
DATABASE_URL = os.getenv("DATABASE_URL")
if not os.path.exists(DATABASE_URL):
    raise FileNotFoundError(f"Database file not found: {DATABASE_URL}")
```

## MCP Resources Implementation

1. Entity Resources
```python
@mcp.resource("entities://list")
def list_entities() -> str:
    """List all entities in the system"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        return cursor.execute("SELECT * FROM entities").fetchall()

@mcp.resource("entities://{entity_id}")
def get_entity(entity_id: str) -> str:
    """Get specific entity details including observations"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        return cursor.execute(
            "SELECT * FROM entities WHERE id = ?", 
            (entity_id,)
        ).fetchone()
```

2. IaC-Specific Resources
```python
@mcp.resource("providers://{provider}/resources")
def list_provider_resources(provider: str) -> str:
    """List all resources for a specific provider"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        return cursor.execute(
            "SELECT * FROM provider_resources WHERE provider_name = ?",
            (provider,)
        ).fetchall()

@mcp.resource("ansible://collections")
def list_ansible_collections() -> str:
    """List all registered Ansible collections"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        return cursor.execute("SELECT * FROM ansible_collections").fetchall()
```

## MCP Tools Implementation

1. Entity Management Tools
```python
@mcp.tool()
def create_entity(name: str, entity_type: str, observations: list[str]) -> str:
    """Create a new entity with initial observations"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        entity_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO entities (id, name, type) VALUES (?, ?, ?)",
            (entity_id, name, entity_type)
        )
        for obs in observations:
            cursor.execute(
                "INSERT INTO observations (entity_id, content) VALUES (?, ?)",
                (entity_id, obs)
            )
        conn.commit()
        return entity_id

@mcp.tool()
def add_observation(entity_id: str, content: str) -> bool:
    """Add a new observation to an existing entity"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO observations (entity_id, content) VALUES (?, ?)",
            (entity_id, content)
        )
        conn.commit()
        return True
```

2. IaC Resource Tools
```python
@mcp.tool()
def register_provider_resource(
    provider: str,
    resource_type: str,
    schema_version: str,
    doc_url: str
) -> str:
    """Register a new provider resource type"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        resource_id = str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO provider_resources 
               (id, provider_name, resource_type, schema_version, doc_url)
               VALUES (?, ?, ?, ?, ?)""",
            (resource_id, provider, resource_type, schema_version, doc_url)
        )
        conn.commit()
        return resource_id

@mcp.tool()
def register_ansible_module(
    collection: str,
    module: str,
    version: str,
    doc_url: str
) -> str:
    """Register a new Ansible module"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        module_id = str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO ansible_collections
               (id, collection_name, module_name, version, doc_url)
               VALUES (?, ?, ?, ?, ?)""",
            (module_id, collection, module, version, doc_url)
        )
        conn.commit()
        return module_id
```

## MCP Prompts Implementation

1. Entity Interaction Prompts
```python
@mcp.prompt()
def entity_creation_guidance() -> str:
    return """To create a new IaC-related entity:
    - Specify name (unique identifier)
    - Entity type (provider, module, resource)
    - Include key observations about usage, requirements, or dependencies
    """

@mcp.prompt()
def observation_guidance() -> str:
    return """When adding observations:
    - Focus on technical details
    - Include version compatibility information
    - Note any deprecation warnings
    - Reference documentation when available
    """
```

2. IaC-Specific Prompts
```python
@mcp.prompt()
def resource_registration_guidance() -> str:
    return """When registering provider resources:
    - Include full resource type path
    - Specify schema version
    - Provide official documentation URL
    - Note any required provider configurations
    """

@mcp.prompt()
def ansible_module_guidance() -> str:
    return """When registering Ansible modules:
    - Include full collection name
    - Specify supported versions
    - List key parameters
    - Note platform compatibility
    """
```

## Testing Plan
1. Unit Tests
   - Resource response validation
   - Tool execution verification
   - Database operation testing
   - Error handling coverage

2. Integration Tests
   - Claude Desktop compatibility
   - Database file handling
   - MCP protocol compliance
   - Resource/Tool interaction flows