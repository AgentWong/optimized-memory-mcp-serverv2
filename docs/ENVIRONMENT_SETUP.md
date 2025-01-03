# Environment Setup Guide

## System Requirements

- Python 3.13.1 or higher
- SQLite 3.x
- Git (for development)

## Python Environment Setup

1. Create Virtual Environment
   ```bash
   python -m venv .venv
   
   # Activate on Unix/macOS
   source .venv/bin/activate
   
   # Activate on Windows
   .venv\Scripts\activate
   ```

2. Install Dependencies
   ```bash
   # Production dependencies
   pip install -r requirements.txt
   
   # Development dependencies (if contributing)
   pip install -r requirements-dev.txt
   ```

## Database Configuration

1. Set Database URL
   ```bash
   # Unix/macOS
   export DATABASE_URL=sqlite:///path/to/your/database.db
   
   # Windows PowerShell
   $env:DATABASE_URL="sqlite:///path/to/your/database.db"
   
   # Windows CMD
   set DATABASE_URL=sqlite:///path/to/your/database.db
   ```

2. Initialize Database
   ```bash
   alembic upgrade head
   ```

## Development Tools Setup

If you plan to contribute to the project:

1. Install Pre-commit Hooks
   ```bash
   pre-commit install
   ```

2. Configure Code Quality Tools
   ```bash
   # Run linting
   flake8
   
   # Run type checking
   mypy .
   
   # Run tests
   pytest
   ```

## Server Configuration

1. Default Settings
   - Host: localhost
   - Port: 8000
   - Workers: 4

2. Custom Configuration
   ```bash
   # Set custom port
   export MCP_PORT=9000
   
   # Set custom host
   export MCP_HOST=0.0.0.0
   
   # Set worker count
   export MCP_WORKERS=8
   ```

## Verification

1. Start Server
   ```bash
   uvx run python -m src.main
   ```

2. Test Connection
   ```bash
   curl http://localhost:8000/health
   ```

3. Run Test Suite
   ```bash
   pytest -v
   ```

## Common Issues

1. Python Version Mismatch
   - Error: "Invalid Python version"
   - Solution: Install Python 3.13.1 or higher

2. Database Connection
   - Error: "Database connection failed"
   - Solution: Verify DATABASE_URL and file permissions

3. Dependencies
   - Error: "Module not found"
   - Solution: Verify all requirements are installed

4. Port Conflicts
   - Error: "Address already in use"
   - Solution: Change port or stop conflicting service

## Next Steps

1. Review [MCP Usage Guide](MCP_USAGE.md)
2. Configure Claude Desktop integration
3. Run example queries
4. Review [API Documentation](API.md)

## Support

For additional help:
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review GitHub issues
3. Contact support team
