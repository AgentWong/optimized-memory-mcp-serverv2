"""
MCP server tools implementation.

This package contains tool implementations that provide action-performing capabilities 
through the MCP protocol. Tools differ from resources in that they can modify state
and perform actions, while resources are read-only.

Key Tool Categories:
- Entity Management: Create, update and delete infrastructure entities
- Observation Management: Record and manage entity observations
- Relationship Management: Define and maintain entity relationships
- Provider Management: Register and configure infrastructure providers
- Ansible Management: Handle Ansible collections and modules
- Analysis: Perform infrastructure analysis and comparisons

Each tool follows MCP protocol patterns:
- Tools are registered with @mcp.tool() decorator
- Tools accept typed parameters and return structured data
- Tools handle errors using standard MCP error types
- Tools integrate with the database through SQLAlchemy sessions
"""
