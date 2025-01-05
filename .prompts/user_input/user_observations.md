/home/herman/Documents/vscode/optimized-memory-mcp-serverv2/.venv/lib/python3.13/site-packages/pytest_asyncio/plugin.py:207: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
============================= test session starts ==============================
platform linux -- Python 3.13.1, pytest-8.3.4, pluggy-1.5.0
rootdir: /home/herman/Documents/vscode/optimized-memory-mcp-serverv2
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.7.0, asyncio-0.25.1, cov-6.0.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None
collected 53 items                                                             

tests/claude/test_claude_compatibility.py 