# Optimized Memory MCP Server v2

A high-performance Python-based Model Context Protocol (MCP) server implementation optimized for Claude Desktop integration. This server provides efficient memory management and robust infrastructure component tracking capabilities.

## Overview

This MCP server implementation focuses on:
- Efficient memory management for large-scale infrastructure tracking
- Comprehensive resource and tool implementations following MCP patterns
- Full Claude Desktop compatibility
- SQLite-based persistent storage with connection pooling
- Robust error handling and resource cleanup

## Features

- **MCP Resources**
  - Entity management (listing, retrieval, relationships)
  - Provider resource tracking
  - Ansible collection management
  - Version tracking
  - Full-text search capabilities

- **MCP Tools**
  - Entity creation and management
  - Observation tracking
  - Provider registration
  - Ansible module integration
  - Infrastructure analysis tools

- **Core Components**
  - FastMCP server implementation
  - SQLite database with connection pooling
  - Comprehensive error handling
  - Automatic resource cleanup
  - Extensive logging

## Project Structure

```
.
├── src/
│   ├── resources/          # MCP resource implementations
│   ├── tools/             # MCP tool implementations
│   ├── db/                # Database management
│   ├── utils/             # Utility functions
│   └── server.py          # Main server implementation
├── tests/
│   ├── resources/         # Resource tests
│   ├── tools/             # Tool tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
├── migrations/            # Database migrations
└── requirements/          # Project dependencies
```

## Requirements

- Python 3.13.1 or higher
- SQLite 3.x
- uvx server

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AgentWong/optimized-memory-mcp-serverv2.git
   cd optimized-memory-mcp-serverv2
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Unix/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. Initialize the database:
   ```bash
   alembic upgrade head
   ```

## Usage

1. Start the server:
   ```bash
   uvx run python -m src.main
   ```

2. Configure Claude Desktop:
   - Set MCP server URL to `http://localhost:8000`
   - Enable MCP protocol in Claude settings

3. Verify connection:
   ```bash
   curl http://localhost:8000/health
   ```

## Development Setup

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Check code quality:
   ```bash
   flake8
   mypy .
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following our conventions
4. Run tests and linting
5. Submit a pull request

## Documentation

- [API Documentation](docs/API.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Claude Desktop team for MCP protocol specifications
- Contributors to the FastMCP library
- SQLAlchemy team for database tooling
