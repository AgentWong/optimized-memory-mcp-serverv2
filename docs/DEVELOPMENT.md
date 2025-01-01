# Development Guide

## Development Environment Setup

Our development environment uses a virtual environment to manage dependencies separately from production requirements. Here's how to set it up:

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install the project in editable mode:
   ```bash
   pip install -e .
   ```

## Code Quality Tools

We use several tools to maintain code quality:

### Flake8
Flake8 is our primary linting tool. It's configured in `.flake8` and includes plugins for docstring checking and import ordering.

Run the linter:
```bash
flake8 src/ tests/
```

### Pytest
All tests are written using pytest. The configuration is in `pytest.ini` and includes coverage reporting.

Run the test suite:
```bash
pytest
```

View coverage report:
```bash
pytest --cov-report html
```

### Code Formatting
We use Black to maintain consistent code formatting:
```bash
black src/ tests/
```

## Development Workflow

1. Create a new branch for your feature or bugfix
2. Write tests first (TDD approach)
3. Implement your changes
4. Run the full test suite
5. Run linting and formatting checks
6. Commit your changes with a descriptive message

## Running the Server

During development, you can run the server directly with uvx:
```bash
uvx run src/main.py
```

For debugging, enable debug mode:
```bash
uvx run src/main.py --debug
```

## MCP Inspector Integration

The MCP Inspector is essential for testing and debugging. To use it:

1. Install the inspector:
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. Run your server with the inspector:
   ```bash
   npx @modelcontextprotocol/inspector uvx run src/main.py
   ```

## Claude Desktop Integration

1. Configure Claude Desktop to use your server:
   ```json
   {
     "mcpServers": {
       "your-server-name": {
         "command": "uvx",
         "args": ["your-package-name"]
       }
     }
   }
   ```

2. Test the integration using the MCP Inspector
3. Verify tool and resource functionality
4. Monitor server logs for any issues

## Common Development Tasks

### Adding a New Resource
1. Create a new module in `src/resources/`
2. Implement the resource using the `@mcp.resource` decorator
3. Add corresponding tests in `tests/resources/`
4. Update documentation if needed

### Adding a New Tool
1. Create a new module in `src/tools/`
2. Implement the tool using the `@mcp.tool` decorator
3. Add corresponding tests in `tests/tools/`
4. Update documentation if needed

## Troubleshooting

Common issues and their solutions:

1. Virtual Environment Issues
   - Verify .venv is activated
   - Check installed packages with `pip list`
   - Rebuild venv if dependencies conflict

2. Test Failures
   - Run specific test with -k flag
   - Use --pdb for debugging
   - Check coverage reports for gaps

3. Linting Errors
   - Run black before flake8
   - Check .flake8 configuration
   - Use # noqa for specific exceptions