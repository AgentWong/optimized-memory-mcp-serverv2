# MCP Usage Guide

## Overview

This guide explains how to use the MCP (Model Context Protocol) server implementation with Claude Desktop and other MCP-compatible clients.

## Basic Concepts

### Resources
MCP resources provide read access to server data through URL-like patterns:

- `entities://list` - List all tracked entities
- `entities://{id}` - Get details for a specific entity
- `providers://{provider}/resources` - List resources for a provider
- `ansible://collections` - List registered Ansible collections

### Tools
MCP tools provide ways to modify server data:

- `create_entity()` - Create new infrastructure entities
- `add_observation()` - Add observations to entities
- `register_provider()` - Register new infrastructure providers
- `register_ansible_module()` - Register Ansible modules

## Getting Started

1. Ensure the MCP server is running:
   ```bash
   uvx run python -m src.main
   ```

2. Configure your DATABASE_URL environment variable:
   ```bash
   export DATABASE_URL=sqlite:///path/to/your/database.db
   ```

3. Configure Claude Desktop:
   - Open Settings
   - Enable MCP Protocol
   - Set Server URL to `http://localhost:8000`
   - Test connection

## Using Resources

### Entity Management
```python
# List all entities
entities = await mcp.get("entities://list")

# Get specific entity
entity = await mcp.get(f"entities://{entity_id}")

# List relationships
rels = await mcp.get("relationships://list")

# Get observations
obs = await mcp.get(f"observations://{entity_id}")
```

### Provider Resources
```python
# List provider resources
resources = await mcp.get(f"providers://{provider}/resources")

# List Ansible collections
collections = await mcp.get("ansible://collections")
```

## Using Tools

### Entity Management
```python
# Create new entity
entity_id = await mcp.tool("create_entity", 
    name="web-server",
    entity_type="server",
    observations=["Ubuntu 22.04", "4 CPU cores"]
)

# Add observation
success = await mcp.tool("add_observation",
    entity_id=entity_id,
    content="Added SSL certificate"
)
```

### Provider Management
```python
# Register provider
provider_id = await mcp.tool("register_provider_resource",
    provider="aws",
    resource_type="ec2_instance",
    schema_version="1.0",
    doc_url="https://docs.aws.amazon.com/..."
)

# Register Ansible module
module_id = await mcp.tool("register_ansible_module",
    collection="ansible.builtin",
    module="copy",
    version="2.9",
    doc_url="https://docs.ansible.com/..."
)
```

## Error Handling

The server provides detailed error messages:

- ConfigurationError - Configuration issues
- DatabaseError - Database operation failures
- ValidationError - Invalid input data
- MCPError - General MCP protocol errors

Example error handling:
```python
try:
    result = await mcp.tool("create_entity", ...)
except ValidationError as e:
    print(f"Invalid input: {e.message}")
    print(f"Details: {e.details}")
except MCPError as e:
    print(f"MCP error: {e.message}")
```

## Best Practices

1. Resource Usage
   - Cache resource results when appropriate
   - Use specific entity IDs instead of listing all
   - Implement pagination for large result sets

2. Tool Usage
   - Validate input before calling tools
   - Handle all potential errors
   - Use appropriate tool for each operation
   - Don't create duplicate entities

3. General Tips
   - Keep database connections short
   - Clean up resources properly
   - Use appropriate error handling
   - Monitor server performance

## Troubleshooting

Common issues and solutions:

1. Connection Errors
   - Verify server is running
   - Check DATABASE_URL setting
   - Ensure ports are open

2. Database Errors
   - Check database file permissions
   - Verify schema version
   - Monitor disk space

3. Tool Failures
   - Validate input data
   - Check error messages
   - Verify required permissions

## Additional Resources

- [API Documentation](API.md)
- [Configuration Guide](CONFIGURATION.md)
- [Database Schema](DATABASE_SCHEMA.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
