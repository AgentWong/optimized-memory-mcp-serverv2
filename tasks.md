# MCP Server Bug Fix Tasks

## Database Schema and Migration Issues
- [x] Task 1: Fix database initialization for test environments
  - Add missing table creation migrations in alembic
  - Ensure test database gets properly initialized
  - Verify SQLite configuration for tests

- [x] Task 2: Complete model attribute definitions
  - Add missing fields to models:
    - Provider: Add 'namespace' field
    - Relationship: Add 'relationship_type' and 'source_id' fields 
    - Observation: Add 'observation_type' field
  - Update model constructors
  - Add field validations
  - Update model tests

## MCP Resource Implementation
- [ ] Task 3: Fix entity resource parameter handling
  - Update get_entity resource function signature to match MCP protocol
  - Ensure proper MCP context usage
  - Add error handling for invalid entity IDs
  - Update resource tests

## Test Infrastructure
- [ ] Task 4: Improve test database setup
  - Create proper test database initialization
  - Add test data fixtures
  - Implement database cleanup between tests
  - Add comprehensive model validation tests

## Documentation
- [ ] Task 5: Update documentation for model changes
  - Document new model fields
  - Update example MCP resource usage
  - Add database migration instructions

Priority Order:
1. Database Schema (Task 1)
2. Model Fixes (Task 2)
3. MCP Resource Implementation (Task 3)
4. Test Infrastructure (Task 4)
5. Documentation (Task 5)

Note: All implementation should follow MCP SDK conventions and avoid any web framework dependencies.
