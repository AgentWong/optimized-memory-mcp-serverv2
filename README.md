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

1. Ensure Python 3.13.1 is installed:
   ```bash
   python --version  # Should show 3.13.1
   ```

2. Install uvx if not already installed:
   ```bash
   pip install uvx
   ```

3. Clone this repository:
   ```bash
   git clone https://github.com/AgentWong/optimized-memory-mcp-serverv2.git
   cd optimized-memory-mcp-serverv2
   ```

4. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

6. Initialize the database:
   ```bash
   alembic upgrade head
   ```

7. Run the server:
   ```bash
   uvx run python -m src.main
   ```

## Development

Follow the conventions outlined in `docs/CONVENTIONS.md` for implementation details and best practices.
