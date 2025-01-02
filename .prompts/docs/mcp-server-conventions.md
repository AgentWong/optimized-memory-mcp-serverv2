# MCP Server Implementation Conventions

## Overview
This document outlines the conventions and requirements for implementing a Model Context Protocol (MCP) server using Python 3.13.1. These guidelines are designed for creating a server that will interface with the Claude Desktop application as an MCP client.

## Server Structure

### Core Components
1. Server Initialization
   - Use `FastMCP` class from the MCP SDK
   - Provide a descriptive server name
   - Define any required dependencies

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Your Server Name", dependencies=["required-packages"])
```

### Resources
Resources are read-only data providers that follow these conventions:

1. Resource Path Format
   - Use URL-like patterns with meaningful prefixes
   - Support dynamic parameters using curly braces
   - Example: `resource://category/{parameter}`

2. Resource Function Structure
   - Use decorator syntax: `@mcp.resource(path)`
   - Include type hints for parameters and return values
   - Provide docstrings for documentation
   - Return data without side effects

```python
@mcp.resource("data://{identifier}")
def get_data(identifier: str) -> str:
    """
    Resource docstring describing the data being provided.
    """
    return f"Data for {identifier}"
```

### Tools
Tools are action-performing components that follow these conventions:

1. Tool Definition
   - Use the `@mcp.tool()` decorator
   - Include complete type hints
   - Provide clear docstrings
   - Can be synchronous or async

2. Tool Function Structure
   - Accept specific input parameters
   - Return well-defined output types
   - Handle errors gracefully
   - Document side effects

```python
@mcp.tool()
async def process_data(input_data: str) -> dict:
    """
    Tool docstring describing the action and its effects.
    """
    # Implementation
    return {"result": "processed"}
```

## Runtime Configuration

### Development Mode
For development and testing:
```python
if __name__ == "__main__":
    mcp.run(dev=True)
```

### Production Mode
For production deployment with uvx:
```python
# server.py
app = mcp.get_application()
```

## Best Practices

### Error Handling
1. Use Python's built-in exception handling
2. Return meaningful error messages
3. Implement proper type checking
4. Handle async operations correctly

### Type Safety
1. Use strict type hints throughout
2. Implement runtime type checking where necessary
3. Document complex type structures
4. Use proper return type annotations

### Documentation
1. Include detailed docstrings for all components
2. Document all parameters and return types
3. Provide usage examples in docstrings
4. Use consistent documentation format

### Security Considerations
1. Validate all input parameters
2. Implement proper error handling
3. Avoid exposing sensitive information
4. Use secure default values

## Integration Points

### Claude Desktop Integration
1. Ensure compatibility with Claude's MCP client implementation
2. Follow standard MCP messaging protocols
3. Implement proper session handling
4. Support required message formats

### Resource Management
1. Implement proper resource cleanup
2. Handle connection timeouts
3. Manage memory efficiently
4. Implement proper logging

## Testing Guidelines

### Unit Tests
1. Test all resource endpoints
2. Test all tools independently
3. Verify error handling
4. Test type validation

### Integration Tests
1. Test complete workflows
2. Verify Claude Desktop compatibility
3. Test resource limitations
4. Verify proper cleanup

## Deployment and Configuration

### UV/UVX Configuration
1. Package Configuration
   - Structure the package to be directly runnable with uvx
   - Implement proper entry points for package execution
   - Define clear package metadata

2. Claude Desktop Integration
   ```json
   "mcpServers": {
     "your-server-name": {
       "command": "uvx",
       "args": ["your-package-name"]
     }
   }
   ```

### Command Line Arguments
1. Standard Arguments
   - Implement standard MCP server arguments
   - Support customization options via CLI
   - Document all available arguments

2. Configuration Parameters
   - Define clear parameter names
   - Support both environment variables and CLI arguments
   - Implement proper argument parsing

### Environment Setup
1. Use Python 3.13.1
2. Manage dependencies with requirements.txt
3. Configure proper logging
4. Set up appropriate error handling

### Performance Optimization
1. Implement caching where appropriate
2. Optimize resource usage
3. Handle concurrent requests properly
4. Monitor memory usage

## Maintenance Guidelines

### Code Organization
1. Use modular structure
2. Separate concerns appropriately
3. Follow consistent naming conventions
4. Implement proper versioning

### Updates and Upgrades
1. Document version changes
2. Maintain backward compatibility
3. Update dependencies safely
4. Test thoroughly before deployment
