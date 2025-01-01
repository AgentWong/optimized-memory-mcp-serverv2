# optimized-memory-mcp-serverv2
This is a personal project to test Claude AI's ability to self-write an MCP Server code for its own use.

This is a Python-based Model Context Protocol (MCP) server implementation designed to work with Claude Desktop as an MCP client.

## Project Structure

```
mcp_server/
├── README.md                 # Project documentation
├── requirements.txt          # Project dependencies
├── server.py                # Main server implementation
├── tests/                   # Test directory
│   ├── __init__.py
│   ├── test_resources.py
│   └── test_tools.py
├── docs/                    # Documentation
│   └── CONVENTIONS.md       # Implementation conventions
└── src/                     # Source code
    ├── __init__.py
    ├── resources/          # Resource implementations
    │   └── __init__.py
    ├── tools/              # Tool implementations
    │   └── __init__.py
    └── utils/              # Utility functions
        └── __init__.py
```

## Getting Started

1. Ensure Python 3.13.1 is installed
2. Install uvx if not already installed
3. Clone this repository
4. Install dependencies: `uvx run --from git+https://github.com/AgentWong/<repo_name>.git python -m <module_name>`

## Development

Follow the conventions outlined in `docs/CONVENTIONS.md` for implementation details and best practices.