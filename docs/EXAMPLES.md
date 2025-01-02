# MCP Server Usage Examples

## Basic Entity Management

### Creating an Entity
```python
import requests

# Create a new entity
response = requests.post("http://localhost:8000/entities", json={
    "name": "aws_instance_1",
    "type": "aws_instance",
    "metadata": {
        "instance_type": "t2.micro",
        "region": "us-west-2"
    }
})
entity = response.json()
entity_id = entity["id"]
```

### Creating Related Entities with Relationships
```python
# Create a security group entity
sg_response = requests.post("http://localhost:8000/entities", json={
    "name": "web_sg",
    "type": "aws_security_group",
    "metadata": {
        "vpc_id": "vpc-123456"
    }
})
sg_id = sg_response.json()["id"]

# Create a relationship between instance and security group
requests.post("http://localhost:8000/relationships", json={
    "source_id": entity_id,
    "target_id": sg_id,
    "type": "uses_security_group",
    "metadata": {
        "added_date": "2025-01-01"
    }
})
```

## Working with Observations

### Adding Observations to Entities
```python
# Record CPU usage observation
requests.post(f"http://localhost:8000/entities/{entity_id}/observations", json={
    "type": "cpu_usage",
    "value": {
        "percentage": 75.5,
        "timestamp": "2025-01-01T12:00:00Z"
    }
})

# Record memory usage observation
requests.post(f"http://localhost:8000/entities/{entity_id}/observations", json={
    "type": "memory_usage",
    "value": {
        "used_mb": 1024,
        "total_mb": 4096,
        "timestamp": "2025-01-01T12:00:00Z"
    }
})
```

## Context and Relationships

### Getting Entity Context
```python
# Get related entities up to 2 levels deep
context = requests.get(
    f"http://localhost:8000/context/related/{entity_id}",
    params={
        "max_depth": 2,
        "include_observations": True,
        "relationship_types": ["uses_security_group", "belongs_to_vpc"]
    }
).json()
```

## Infrastructure Provider Integration

### Analyzing Provider Version Changes
```python
# Compare provider versions
analysis = requests.get(
    "/providers/1/analysis",
    params={
        "from_version": "4.50.0",
        "to_version": "4.51.0"
    }
).json()

# Check for breaking changes
breaking_changes = [
    change for change in analysis["changes"]
    if change["severity"] == "breaking"
]
```

### Checking Ansible Collection Compatibility
```python
# Verify collection compatibility
compatibility = requests.get(
    "/ansible/community.aws/compatibility",
    params={
        "version": "3.5.0"
    }
).json()

# Check supported provider versions
supported_versions = compatibility["supported_provider_versions"]
```

## Search and Query

### Finding Related Resources
```python
# Search for all EC2 instances in a VPC
results = requests.get(
    "/search",
    params={
        "type": "aws_instance",
        "metadata.vpc_id": "vpc-123456"
    }
).json()

# Get all security groups used by an instance
security_groups = requests.get(
    "/search",
    params={
        "type": "aws_security_group",
        "related_to": entity_id,
        "relationship_type": "uses_security_group"
    }
).json()
```

### Checking for Deprecations
```python
# Check for deprecated features in provider version
deprecations = requests.get(
    "/providers/1/deprecations",
    params={
        "version": "4.51.0"
    }
).json()

# Get deprecation warnings for specific resources
resource_deprecations = [
    d for d in deprecations
    if d["resource_type"] in ["aws_instance", "aws_security_group"]
]
```

## Error Handling Example
```python
try:
    response = requests.post("http://localhost:8000/entities", json={
        "name": "invalid_entity",
        # Missing required 'type' field
    })
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    error_data = e.response.json()
    print(f"Error code: {error_data['code']}")
    print(f"Message: {error_data['message']}")
    print(f"Details: {error_data['details']}")
```

## Best Practices

1. Always check response status codes and handle errors appropriately
2. Use meaningful entity names and types
3. Include relevant metadata with entities and relationships
4. Set appropriate relationship types
5. Include timestamps with observations
6. Use the context API to efficiently retrieve related data
7. Implement proper error handling
8. Use search parameters effectively to filter results
9. Check for deprecations when upgrading providers
10. Validate compatibility before updating collections
