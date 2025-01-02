# MCP Server Configuration Guide

## Overview
This guide covers all configuration options for the MCP Server, including environment variables, database settings, server configuration, and logging options.

## Environment Variables

### Database Configuration
- `DATABASE_URL` (string)
  - Default: `sqlite:///mcp_server.db`
  - Format: SQLAlchemy URL string
  - Examples:
    ```bash
    # SQLite (default)
    export DATABASE_URL="sqlite:///mcp_server.db"
    
    # SQLite with custom path
    export DATABASE_URL="sqlite:///path/to/custom/mcp_server.db"
    
    # SQLite with connection pooling
    export DATABASE_URL="sqlite:///mcp_server.db?timeout=30&pool_size=20"
    ```

### Server Settings
- `MCP_HOST` (string)
  - Default: `127.0.0.1`
  - The IP address or hostname to bind the server
  - Example: `export MCP_HOST="0.0.0.0"`

- `MCP_PORT` (integer)
  - Default: `8000`
  - The port number to listen on
  - Example: `export MCP_PORT="9000"`

- `MCP_DEBUG` (boolean)
  - Default: `0` (false)
  - Enable debug mode (1/true) or disable (0/false)
  - Example: `export MCP_DEBUG="1"`

### Logging Configuration
- `MCP_LOG_LEVEL` (string)
  - Default: `INFO`
  - Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - Example: `export MCP_LOG_LEVEL="DEBUG"`

## Configuration Files

### pyproject.toml
The project uses pyproject.toml for Python package configuration:

```toml
[tool.black]
line-length = 88
target-version = ['py313']

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --cov=src"
testpaths = ["tests"]
```

### .flake8
Code style checking configuration:

```ini
[flake8]
max-line-length = 88
extend-ignore = E203
max-complexity = 10
docstring-convention = google
import-order-style = google
application-import-names = src,tests
```

## Development Tools Configuration

### Code Formatting
The project uses Black for code formatting:
```bash
# Format all Python files
black .

# Check formatting without changes
black --check .
```

### Type Checking
MyPy is configured for strict type checking:
```bash
# Run type checking
mypy src tests

# Generate HTML report
mypy --html-report mypy_report src tests
```

### Linting
Flake8 is configured for code style checking:
```bash
# Run linting
flake8 src tests

# Show specific error codes
flake8 --select E,W,F src tests
```

## Production Deployment

### Security Considerations
1. Database:
   - Use a production-grade database system
   - Configure proper authentication
   - Enable SSL/TLS for database connections
   - Set appropriate connection pool sizes

2. Server:
   - Run behind a reverse proxy (nginx/Apache)
   - Enable HTTPS
   - Set appropriate worker processes
   - Configure rate limiting

3. Environment:
   - Use secure environment variable management
   - Rotate sensitive credentials regularly
   - Monitor log levels appropriately
   - Configure backup systems

### Example Production Configuration
```bash
# Production environment variables
export DATABASE_URL="postgresql://user:pass@db.example.com/mcp_db?sslmode=require"
export MCP_HOST="0.0.0.0"
export MCP_PORT="8000"
export MCP_DEBUG="0"
export MCP_LOG_LEVEL="WARNING"
```

## Monitoring and Logging

### Log Format
The default log format is:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Log Levels
1. DEBUG: Detailed information for debugging
2. INFO: General operational information
3. WARNING: Minor issues that don't affect operation
4. ERROR: Serious issues that affect operation
5. CRITICAL: Critical issues requiring immediate attention

## Performance Tuning

### Database Optimization
1. Connection Pool Settings:
   - Minimum connections
   - Maximum connections
   - Connection timeout
   - Pool recycle time

2. Query Optimization:
   - Index usage
   - Query planning
   - Result caching

### Server Optimization
1. Worker Processes:
   - Number of workers
   - Worker class
   - Worker timeout

2. Resource Limits:
   - Maximum requests
   - Request timeout
   - Keep-alive timeout

## Troubleshooting

### Common Issues

1. Database Connection:
```bash
# Check database connection
python -c "from src.db.connection import get_db; next(get_db())"
```

2. Server Binding:
```bash
# Check port availability
nc -zv localhost 8000
```

3. Configuration Loading:
```bash
# Verify environment variables
python -c "from src.config import Config; print(Config.as_dict())"
```
