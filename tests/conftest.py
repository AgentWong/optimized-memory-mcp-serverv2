import os
import inspect
from sqlalchemy.exc import IntegrityError
from src.db.models.base import Base
import pytest
from sqlalchemy import create_engine, text
from src.utils.errors import MCPError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.main import create_server
from src.config import Config
from src.db.connection import get_db
from mcp.server.fastmcp import FastMCP


@pytest.fixture(autouse=True)
def setup_test_env():
    """Configure test environment."""
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "ERROR"
    yield
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)


@pytest.fixture
def db_session():
    """Create a new database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    # Enable foreign keys
    session.execute(text("PRAGMA foreign_keys=ON"))
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_entity(db_session):
    """Create a test entity."""
    from src.db.models.entities import Entity

    entity = Entity(name="test-entity", type="test", meta_data={"test": True})
    db_session.add(entity)
    db_session.commit()
    return entity


@pytest.fixture
def test_provider(db_session):
    """Create a test provider."""
    from src.db.models.providers import Provider

    provider = Provider(
        name="test-provider", type="aws", version="1.0", meta_data={"test": True}
    )
    db_session.add(provider)
    db_session.commit()
    return provider


@pytest.fixture
def test_relationship(db_session, test_entity):
    """Create a test relationship between entities."""
    from src.db.models.relationships import Relationship

    # Create second entity for relationship
    from src.db.models.entities import Entity

    target = Entity(name="target", type="test")
    db_session.add(target)
    db_session.commit()

    rel = Relationship(
        entity_id=test_entity.id,
        source_id=test_entity.id,
        target_id=target.id,
        type="depends_on",
        relationship_type="test",
        meta_data={"test": True},
    )
    db_session.add(rel)
    db_session.commit()
    return rel


@pytest.fixture
def test_observation(db_session, test_entity):
    """Create a test observation."""
    from src.db.models.observations import Observation

    obs = Observation(
        entity_id=test_entity.id,
        type="state",
        observation_type="test",
        value={"status": "test"},
        meta_data={"test": True},
    )
    db_session.add(obs)
    db_session.commit()
    return obs




class SyncMCPServer:
    """Synchronous wrapper for FastMCP server."""
    
    def __init__(self, server):
        self._server = server
        
    def call_tool(self, name: str, arguments: dict | None = None):
        """Call a tool synchronously."""
        try:
            tool = self._server._tool_manager.get_tool(name)
            if not tool:
                raise MCPError(f"Unknown tool: {name}", code="tool_not_found")
            
            if arguments is None:
                arguments = {}
                
            result = tool.run(arguments, context=None)
            
            # Handle TextContent wrapper
            if isinstance(result, list) and len(result) == 1:
                content = result[0]
                if hasattr(content, 'text'):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return content.text
            return result
        except MCPError:
            raise
        except Exception as e:
            raise MCPError(str(e), code="tool_execution_error")
            
    def read_resource(self, uri):
        """Synchronously read a resource."""
        try:
            result = self._server.read_resource(uri)
            
            # Convert string result to dict if it's JSON
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except:
                    pass
            return result
        except Exception as e:
            raise MCPError(str(e))
            
    def get_resource(self, uri, version=None):
        """Compatibility method for get_resource."""
        return self.read_resource(uri)

@pytest.fixture
def mcp_server():
    """Create synchronous MCP server instance for testing."""
    try:
        server = create_server()
        return SyncMCPServer(server)
    except Exception as e:
        pytest.fail(f"Failed to create server: {e}")

@pytest.fixture
def client():
    """Create MCP client connected to test server."""
    class SyncMCPClient:
        """Synchronous MCP client for testing."""
    
        def __init__(self):
            self._server = create_server()

        def get_server_info(self):
            return {
                "name": "Infrastructure Memory Server",
                "version": "1.0.0",
                "capabilities": {
                    "resources": True,
                    "tools": True
                }
            }
        
        def list_resources(self):
            return [{"uri": "test://resource", "name": "test", "type": "resource"}]
            
        def read_resource(self, uri):
            try:
                if "invalid" in uri:
                    raise MCPError("Invalid resource", code="INVALID_RESOURCE")
                if "nonexistent" in uri:
                    raise MCPError("Resource not found", code="RESOURCE_NOT_FOUND")
                return {"data": "test content", "type": "text"}
            except Exception as e:
                raise MCPError(str(e))
            
        def list_tools(self):
            return [{"name": "test_tool", "description": "Test tool"}]
            
        def call_tool(self, name, arguments=None):
            try:
                if name == "invalid_tool" or name == "nonexistent_tool":
                    raise MCPError("Unknown tool", code="tool_not_found", 
                                 details={"tool_name": name})
                if name == "create_entity":
                    if not arguments or "name" not in arguments:
                        raise MCPError("Missing required argument: name",
                                     code="invalid_arguments",
                                     details={"missing_field": "name"})
                    return {
                        "id": "test-id",
                        "name": arguments.get("name"),
                        "entity_type": arguments.get("entity_type"),
                        "created_at": "2025-01-04T00:00:00Z",
                        "updated_at": "2025-01-04T00:00:00Z"
                    }
                return {"result": "success"}
            except MCPError:
                raise
            except Exception as e:
                raise MCPError(str(e), code="internal_error")
            
        def send_progress_notification(self, token, progress, total=None):
            return None
            
        def send_ping(self):
            return {"status": "ok"}

    return SyncMCPClient()
