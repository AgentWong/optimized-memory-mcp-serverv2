# MCP Server API Documentation

## Overview
The MCP Server provides a RESTful API for managing infrastructure resources, relationships, and observations. This document details all available endpoints, their parameters, and expected responses.

## Base URL
All API endpoints are relative to: `/api/v1`

## Authentication
Authentication requirements are handled by the Claude Desktop client. The MCP server expects proper authentication headers to be present in all requests.

## Common Response Formats

### Success Response
```json
{
    "data": <response_data>,
    "status": "success"
}
```

### Error Response
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {}
    },
    "status": "error"
}
```

## Endpoints

### Entity Management
#### GET /entities
List all entities, optionally filtered by type.

Query Parameters:
- `entity_type` (optional): Filter by entity type
- `limit` (optional): Maximum number of results to return
- `offset` (optional): Number of results to skip

#### POST /entities
Create a new entity.

Request Body:
```json
{
    "name": "string",
    "entity_type": "string",
    "description": "string (optional)"
}
```

### Relationship Management
#### GET /relationships
List relationships between entities.

Query Parameters:
- `source_id` (optional): Filter by source entity
- `target_id` (optional): Filter by target entity
- `relationship_type` (optional): Filter by type

#### POST /relationships
Create a new relationship between entities.

Request Body:
```json
{
    "source_id": "integer",
    "target_id": "integer",
    "relationship_type": "string",
    "description": "string (optional)"
}
```

### Observation Management
#### GET /observations
List observations for entities.

Query Parameters:
- `entity_id` (optional): Filter by entity
- `observation_type` (optional): Filter by type
- `limit` (optional): Maximum number of results
- `offset` (optional): Number of results to skip

#### POST /observations
Create a new observation.

Request Body:
```json
{
    "entity_id": "integer",
    "observation_type": "string",
    "content": "string",
    "metadata": "object (optional)"
}
```

### Context Retrieval
#### GET /context/entity/{entity_id}
Get full context for an entity.

Query Parameters:
- `include_relationships` (optional): Include related entities
- `include_observations` (optional): Include observations
- `relationship_types` (optional): Filter by relationship types
- `observation_types` (optional): Filter by observation types

### Provider Management
#### GET /providers
List infrastructure providers.

#### POST /providers
Register a new provider.

Request Body:
```json
{
    "name": "string",
    "provider_type": "string",
    "version": "string",
    "configuration": "object"
}
```

### Ansible Integration
#### GET /ansible/collections
List available Ansible collections.

#### POST /ansible/collections
Register a new Ansible collection.

Request Body:
```json
{
    "name": "string",
    "version": "string",
    "description": "string",
    "dependencies": "array"
}
```

### Version Management
#### GET /versions/collections/{collection_name}
Get version history for a collection.

#### POST /versions/collections/{collection_name}/versions
Add a new version for a collection.

Request Body:
```json
{
    "version": "string",
    "changes": "array",
    "dependencies": "array"
}
```

### Search and Analysis
#### GET /search/entities
Search across entities.

Query Parameters:
- `query`: Search string
- `entity_type` (optional): Filter by type
- `limit` (optional): Maximum results

#### GET /analysis/providers/{provider_id}
Analyze provider version changes.

Query Parameters:
- `from_version`: Starting version
- `to_version`: Ending version

## Error Codes

- `INVALID_REQUEST`: Malformed request or invalid parameters
- `NOT_FOUND`: Requested resource not found
- `VALIDATION_ERROR`: Data validation failed
- `DATABASE_ERROR`: Database operation failed
- `INTERNAL_ERROR`: Unexpected server error

## Rate Limiting

The API implements rate limiting based on:
- 1000 requests per hour per client
- 10 concurrent requests per client

## Best Practices

1. Use appropriate HTTP methods for operations
2. Include relevant error handling
3. Implement proper pagination for list endpoints
4. Cache responses when appropriate
5. Use batch operations when possible

## Versioning

The API follows semantic versioning. Breaking changes will result in a new major version number.

## Support

For issues or questions about the API:
1. Check the troubleshooting guide
2. Review error documentation
3. Contact support through Claude Desktop
