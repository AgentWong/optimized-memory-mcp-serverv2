# API Endpoints Documentation

## Core Memory API

### Entities
- `GET /entities/{entity_id}`
  - Get details of a specific entity
  - Parameters:
    - `entity_id`: Integer ID of the entity
  - Returns: Entity details including metadata

- `POST /entities`
  - Create a new entity
  - Body: Entity creation parameters
  - Returns: Created entity details

### Relationships
- `GET /related/{entity_id}`
  - Get related entities
  - Parameters:
    - `entity_id`: Integer ID of the entity
    - `relationship_types` (optional): List of relationship types to filter
    - `include_observations`: Boolean to include observations
    - `max_depth`: Integer maximum depth to traverse
  - Returns: List of related entities and their relationships

### Observations
- `GET /observations/{entity_id}`
  - Get observations for an entity
  - Parameters:
    - `entity_id`: Integer ID of the entity
  - Returns: List of observations

## IaC-Specific API

### Providers
- `GET /providers/{provider_id}/analysis`
  - Analyze provider versions
  - Parameters:
    - `provider_id`: Integer ID of the provider
    - `from_version`: Starting version string
    - `to_version`: Target version string
  - Returns: Version analysis results

- `GET /providers/{provider_id}/compatibility`
  - Check provider compatibility
  - Parameters:
    - `provider_id`: Integer ID of the provider
    - `version`: Version string to check
  - Returns: Compatibility status and details

- `GET /providers/{provider_id}/deprecations`
  - Get provider deprecation notices
  - Parameters:
    - `provider_id`: Integer ID of the provider
    - `version` (optional): Specific version to check
  - Returns: List of deprecation notices

### Ansible Collections
- `GET /ansible/{collection_name}/analysis`
  - Analyze collection versions
  - Parameters:
    - `collection_name`: Name of the Ansible collection
    - `from_version`: Starting version string
    - `to_version`: Target version string
  - Returns: Version analysis results

- `GET /ansible/{collection_name}/compatibility`
  - Check collection compatibility
  - Parameters:
    - `collection_name`: Name of the Ansible collection
    - `version`: Version string to check
  - Returns: Compatibility status and details

- `GET /ansible/{collection_name}/deprecations`
  - Get collection deprecation notices
  - Parameters:
    - `collection_name`: Name of the Ansible collection
    - `version` (optional): Specific version to check
  - Returns: List of deprecation notices

## Database Connection Pool Configuration

The API uses SQLite connection pooling with these default settings:
- Pool Size: 20 connections
- Max Overflow: 30 connections 
- Pool Timeout: 30 seconds
- Pool Recycle: 3600 seconds

To modify these settings, update the DATABASE_URL environment variable:
```
sqlite:///mcp_server.db?pool_size=20&max_overflow=30&pool_timeout=30&pool_recycle=3600
```

## Error Responses
All endpoints may return the following error responses:

- `400 Bad Request`
  - Invalid parameters or request body
  - Returns: Error details with code and message

- `404 Not Found`
  - Requested resource not found
  - Returns: Error details with code and message

- `500 Internal Server Error`
  - Server-side error occurred
  - Returns: Error details with code and message

Example error response:
```json
{
    "code": "RESOURCE_NOT_FOUND",
    "message": "Entity with ID 123 not found",
    "details": {
        "entity_id": 123
    }
}
```
