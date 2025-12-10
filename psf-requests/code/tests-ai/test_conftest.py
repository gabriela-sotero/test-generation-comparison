"""
Shared fixtures and configuration for the test suite.
"""
import pytest
from unittest.mock import Mock, MagicMock
from io import BytesIO

from requests.structures import CaseInsensitiveDict
from requests.cookies import RequestsCookieJar


@pytest.fixture
def mock_response():
    """Create a mock urllib3 response object."""
    resp = Mock()
    resp.status = 200
    resp.headers = {}
    resp.reason = 'OK'
    resp._original_response = Mock()
    resp._original_response.msg = Mock()
    resp._original_response.msg.items = Mock(return_value=[])
    resp.stream = Mock(return_value=[b'test data'])
    resp.read = Mock(return_value=b'test data')
    resp.release_conn = Mock()
    return resp


@pytest.fixture
def mock_adapter():
    """Create a mock adapter for testing."""
    adapter = Mock()
    adapter.send = Mock()
    adapter.close = Mock()
    return adapter


@pytest.fixture
def sample_headers():
    """Sample HTTP headers."""
    return {
        'Content-Type': 'application/json',
        'Content-Length': '100',
        'Server': 'TestServer/1.0'
    }


@pytest.fixture
def sample_cookies():
    """Sample cookie jar."""
    jar = RequestsCookieJar()
    jar.set('session_id', 'abc123', domain='example.com', path='/')
    jar.set('user', 'testuser', domain='example.com', path='/')
    return jar


@pytest.fixture
def mock_pool_manager():
    """Mock PoolManager for adapter tests."""
    pm = Mock()
    pm.connection_from_url = Mock()
    pm.clear = Mock()
    return pm
