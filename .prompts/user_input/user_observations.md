- "mcp.testing" is not a valid module of the MCP SDK and no attempts should be made to add it to any testing.
- The AI keeps trying to add FastAPI, API, and HTTP related code despite "no-fastapi.xml" rules directing it not to, ensure nothing you create adds any references to these.

The problem is more complex than just awaiting in the fixture. We need to:

1. Make sure the fixture is properly marked as async
2. Handle the server creation properly in the fixture
3. Make sure the test client can handle the async server initialization