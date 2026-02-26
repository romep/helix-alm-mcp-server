"""Pytest configuration and fixtures for Helix ALM MCP Server tests."""

import asyncio

import pytest
import pytest_asyncio
from helix_alm_mcp.client import HelixALMClient
from helix_alm_mcp.config import settings


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture
async def client():
    """Create authenticated Helix ALM client.

    This fixture creates a client and authenticates it before each test.
    The client is shared within a test but not across tests.
    """
    _client = HelixALMClient()
    await _client.authenticate()
    yield _client
    await _client.close()


@pytest.fixture(autouse=True)
def reset_helix_client(request):
    """Reset the helix_client singleton before each integration test.

    The server module creates a singleton client that can have a stale
    event loop between tests. This fixture resets it.

    Only applies to integration tests (tests in tests/integration/).
    """
    # Only reset for integration tests
    if "integration" in str(request.fspath):
        from helix_alm_mcp import server
        # Reset the singleton client's HTTP client so it creates a new one
        server.helix_client._http_client = None
        server.helix_client._access_token = None
    yield


@pytest.fixture(autouse=True)
async def api_request_delay():
    """Add a delay between tests to avoid API rate limiting.

    Delay value is configured via settings.test_inter_request_delay
    (env var: TEST_INTER_REQUEST_DELAY, default: 0.5s).
    """
    yield
    await asyncio.sleep(settings.test_inter_request_delay)
