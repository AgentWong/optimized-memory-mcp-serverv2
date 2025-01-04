- "mcp.testing" is not a valid module of the MCP SDK and no attempts should be made to add it to any testing.
- The AI keeps trying to add FastAPI, API, and HTTP related code despite "no-fastapi.xml" rules directing it not to, ensure nothing you create adds any references to these.
- In the past 10+ iterations you appear to be going in a continual loop of 1) Adding query parameters and then 2) Remov
ing the query parameters because it is not needed for the MCP resources.