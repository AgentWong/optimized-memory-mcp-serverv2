# MCP Server Installation Guide

## Prerequisites

- Python 3.13.1 or higher
- pip package manager
- Git (for cloning the repository)
- SQLite 3 (default database)

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp-server.git
cd mcp-server
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

3. Install production dependencies:
```bash
pip install -r requirements.txt
```

4. For development, install additional dependencies:
```bash
pip install -r requirements-dev.txt
```

5. Initialize the database:
```bash
python -m src.db.init_db
```

## Configuration

1. Environment Variables:
```bash
# Required
export DATABASE_URL="sqlite:///mcp_server.db"  # Default SQLite database
export MCP_HOST="127.0.0.1"  # Server host
export MCP_PORT="8000"       # Server port

# Optional
export MCP_DEBUG="0"         # Enable debug mode (0/1)
export MCP_LOG_LEVEL="INFO"  # Logging level
```

2. Development Configuration:
- Linting: Use `flake8` for code style checking
- Formatting: Use `black` for code formatting
- Type checking: Use `mypy` for static type analysis

## Running the Server

1. Start the server:
```bash
uvx src.main:app
```

2. Development mode:
```bash
uvx src.main:app --reload
```

3. Running tests:
```bash
pytest
```

## Verification

1. Check server status:
```bash
curl http://localhost:8000/health
```

2. Verify database connection:
```bash
python -c "from src.db.connection import get_db; next(get_db())"
```

## Troubleshooting

Common issues and solutions:

1. Database initialization fails:
   - Ensure proper permissions on the database directory
   - Verify DATABASE_URL environment variable
   - Check SQLite installation

2. Import errors:
   - Verify Python version (3.13.1+)
   - Confirm all dependencies are installed
   - Check virtual environment activation

3. Server won't start:
   - Verify port availability
   - Check host configuration
   - Ensure proper permissions

## Updating

To update the MCP Server:

1. Pull latest changes:
```bash
git pull origin main
```

2. Update dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. Run database migrations:
```bash
alembic upgrade head
```

## Security Notes

1. Production Deployment:
   - Use a production-grade database
   - Configure proper authentication
   - Set secure environment variables
   - Use HTTPS in production

2. Default Settings:
   - Change default database location
   - Update default port if needed
   - Configure proper logging
   - Set appropriate rate limits

## Next Steps

After installation:
1. Review the API documentation in docs/API.md
2. Check usage examples in docs/EXAMPLES.md
3. Configure your environment based on needs
4. Run the test suite to verify installation
