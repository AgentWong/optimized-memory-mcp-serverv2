# MCP Server Troubleshooting Guide

## Common Issues and Solutions

### Database Connection Issues

#### Problem: Unable to Connect to Database
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

**Solutions:**
1. Check database URL configuration:
   ```bash
   echo $DATABASE_URL
   ```
2. Verify database directory permissions
3. Ensure database migrations are run:
   ```bash
   alembic upgrade head
   ```

#### Problem: Connection Pool Exhausted
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
```

**Solutions:**
1. Check for connection leaks in code
2. Adjust pool settings in database URL:
   ```bash
   export DATABASE_URL="sqlite:///mcp_server.db?timeout=30&pool_size=20&max_overflow=30"
   ```

### Server Startup Issues

#### Problem: Address Already in Use
```
OSError: [Errno 98] Address already in use
```

**Solutions:**
1. Check if another process is using the port:
   ```bash
   lsof -i :8000
   ```
2. Kill the existing process or use a different port:
   ```bash
   export MCP_PORT=8001
   ```

#### Problem: Import Errors on Startup
```
ModuleNotFoundError: No module named 'mcp_sdk'
```

**Solutions:**
1. Verify virtual environment is activated:
   ```bash
   which python
   ```
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### API Issues

#### Problem: 500 Internal Server Error
Common causes:
- Database connection issues
- Unhandled exceptions
- Configuration errors

**Solutions:**
1. Check server logs:
   ```bash
   tail -f mcp_server.log
   ```
2. Enable debug mode:
   ```bash
   export MCP_DEBUG=1
   ```
3. Verify configuration:
   ```python
   from src.config import Config
   print(Config.as_dict())
   ```

#### Problem: 404 Not Found Errors
Common causes:
- Incorrect API endpoint URLs
- Missing route handlers
- Database record not found

**Solutions:**
1. Verify API endpoint path
2. Check if database record exists
3. Enable debug logging:
   ```bash
   export MCP_LOG_LEVEL=DEBUG
   ```

### Performance Issues

#### Problem: Slow Query Response Times
Common causes:
- Missing database indexes
- Inefficient queries
- Connection pool issues

**Solutions:**
1. Check database indexes
2. Enable SQL query logging:
   ```bash
   export MCP_LOG_LEVEL=DEBUG
   ```
3. Monitor database connections:
   ```bash
   # Check SQLite database locks
   fuser mcp_server.db
   # View SQLite database status
   sqlite3 mcp_server.db ".dbinfo"
   ```

#### Problem: High Memory Usage
Common causes:
- Large result sets
- Memory leaks
- Connection pool growth

**Solutions:**
1. Monitor memory usage:
   ```bash
   ps aux | grep python
   ```
2. Implement pagination for large results
3. Check for resource cleanup in code

### Development Environment Issues

#### Problem: Linting/Type Checking Errors
```
mypy: error: ...
flake8: ...
```

**Solutions:**
1. Run formatters:
   ```bash
   black .
   ```
2. Update type hints:
   ```bash
   mypy src tests
   ```
3. Fix style issues:
   ```bash
   flake8 src tests
   ```

#### Problem: Test Failures
Common causes:
- Database state issues
- Configuration problems
- Code changes breaking tests

**Solutions:**
1. Reset test database:
   ```bash
   alembic downgrade base
   alembic upgrade head
   ```
2. Run specific test:
   ```bash
   pytest tests/specific_test.py -v
   ```
3. Check test configuration:
   ```bash
   pytest --setup-show tests/
   ```

## Debugging Tips

### Enable Debug Logging
```bash
export MCP_DEBUG=1
export MCP_LOG_LEVEL=DEBUG
```

### Check Configuration
```python
from src.config import Config
print(Config.as_dict())
```

### Database Verification
```bash
# Check database connection
python -c "from src.db.connection import get_db; next(get_db())"

# View database migrations
alembic history
```

### Server Status
```bash
# Check process
ps aux | grep python

# Check port
nc -zv localhost 8000

# View logs
tail -f mcp_server.log
```

## Getting Help

If you continue to experience issues:

1. Check the existing GitHub issues
2. Include in your report:
   - Error messages and stack traces
   - Server logs
   - Configuration settings (sanitized)
   - Steps to reproduce
   - Environment details:
     ```bash
     python --version
     pip freeze
     ```

## Prevention

### Best Practices
1. Regular database backups
2. Monitoring and alerting setup
3. Regular dependency updates
4. Comprehensive testing
5. Configuration management
6. Log rotation and management

### Maintenance
1. Regular database maintenance
2. Log file cleanup
3. Configuration review
4. Security updates
5. Performance monitoring
