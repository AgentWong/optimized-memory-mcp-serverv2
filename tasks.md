# MCP Server Implementation Tasks

## Phase 1: Code Cleanup [⬜]

### Remove REST API Code [⬜]
- [ ] Remove FastAPI dependencies and imports
- [ ] Delete API endpoint definitions
- [ ] Remove API-specific error handlers
- [ ] Clean up API documentation files

### Restructure Project [⬜]
- [ ] Update project structure to MCP patterns
- [ ] Move database code to utils module
- [ ] Create resources package
- [ ] Create tools package

## Phase 2: MCP Server Implementation [⬜]

### Core Setup [⬜]
- [ ] Create FastMCP server instance
- [ ] Configure DATABASE_URL handling
- [ ] Set up SQLite connection management
- [ ] Implement error handling

### Resource Implementation [⬜]

#### Entity Resources [x]
- [x] Convert GET /entities to entities://list resource
- [x] Convert GET /entities/{id} to entities://{id} resource
- [x] Convert GET /relationships to relationships://{id} resource
- [x] Convert GET /observations to observations://{id} resource

#### IaC Resources [⬜]
- [x] Convert GET /providers to providers://{provider}/resources resource
- [x] Convert GET /ansible/collections to ansible://collections resource
- [x] Convert GET /versions/collections to collections://{name}/versions resource
- [x] Convert GET /search/entities to search://{query} resource

### Tool Implementation [⬜]

#### Entity Management Tools [x]
- [x] Convert POST /entities to create_entity() tool
- [x] Convert PUT /entities/{id} to update_entity() tool
- [x] Convert DELETE /entities/{id} to delete_entity() tool
- [x] Convert POST /observations to add_observation() tool

#### IaC Management Tools [⬜]
- [ ] Convert POST /providers to register_provider() tool
- [ ] Convert POST /ansible/collections to register_collection() tool
- [ ] Convert POST /versions/collections to add_version() tool
- [ ] Convert GET /analysis/providers to analyze_provider() tool

## Phase 3: Database Integration [⬜]

### Core Database [⬜]
- [ ] Verify SQLite schema compatibility
- [ ] Update database utility functions
- [ ] Implement connection pooling
- [ ] Add error handling

### Query Optimization [⬜]
- [ ] Optimize entity queries
- [ ] Improve relationship lookups
- [ ] Enhance observation retrieval
- [ ] Add proper indexing

## Phase 4: Testing [⬜]

### Unit Tests [⬜]
- [ ] Test MCP resources
- [ ] Test MCP tools
- [ ] Test database operations
- [ ] Test error handling

### Integration Tests [⬜]
- [ ] Test Claude Desktop compatibility
- [ ] Verify database operations
- [ ] Test resource patterns
- [ ] Validate tool execution

## Phase 5: Documentation [⬜]

### Code Documentation [⬜]
- [ ] Update docstrings for MCP patterns
- [ ] Document resource implementations
- [ ] Document tool implementations
- [ ] Add usage examples

### User Documentation [⬜]
- [ ] Update README.md
- [ ] Create MCP usage guide
- [ ] Document environment setup
- [ ] Add troubleshooting guide

Dependencies:
- REST API removal must be completed first
- Database compatibility must be verified before MCP implementation
- Resources must be implemented before tools
- All features must be tested with Claude Desktop

Notes:
- Follow MCP SDK patterns exactly
- Keep files under 250 lines
- Use only DATABASE_URL environment variable
- Focus on proper MCP Tools and Resources implementation
- Ensure backward compatibility with existing database
