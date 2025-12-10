"""
Integration tests for requests library.
Tests the interaction between multiple components.
"""
import pytest
from unittest.mock import Mock, patch

from requests import Session, Request
from requests.models import PreparedRequest, Response
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict
from requests.cookies import RequestsCookieJar


class TestSessionRequestFlow:
    """Integration tests for Session request flow."""
    
    def test_session_request_full_flow(self):
        """Test complete request flow through session."""
        session = Session()
        
        # Mock the adapter send
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.headers = CaseInsensitiveDict({'Content-Type': 'application/json'})
        mock_response.url = 'http://example.com'
        mock_response._content = b'{"key": "value"}'
        mock_response._content_consumed = True
        
        with patch.object(HTTPAdapter, 'send', return_value=mock_response):
            response = session.get('http://example.com')
            
            assert response.status_code == 200
            assert response.url == 'http://example.com'
    
    def test_session_merges_headers_correctly(self):
        """Test that session merges headers from multiple sources."""
        session = Session()
        session.headers['X-Session'] = 'session-value'
        
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b''
        mock_response._content_consumed = True
        
        with patch.object(HTTPAdapter, 'send', return_value=mock_response) as mock_send:
            session.get('http://example.com', headers={'X-Request': 'request-value'})
            
            # Get the PreparedRequest that was sent
            sent_request = mock_send.call_args[0][0]
            assert 'X-Session' in sent_request.headers
            assert 'X-Request' in sent_request.headers
    
    def test_session_persists_cookies_across_requests(self):
        """Test that session persists cookies across requests."""
        session = Session()
        
        # First response sets cookie
        resp1 = Response()
        resp1.status_code = 200
        resp1.headers = CaseInsensitiveDict({'Set-Cookie': 'session=abc123'})
        resp1._content = b''
        resp1._content_consumed = True
        resp1.cookies = RequestsCookieJar()
        resp1.cookies.set('session', 'abc123')
        
        # Second response
        resp2 = Response()
        resp2.status_code = 200
        resp2._content = b''
        resp2._content_consumed = True
        
        with patch.object(HTTPAdapter, 'send') as mock_send:
            mock_send.side_effect = [resp1, resp2]
            
            session.get('http://example.com/login')
            session.get('http://example.com/profile')
            
            # Second request should have cookie
            second_call_request = mock_send.call_args_list[1][0][0]
            assert isinstance(session.cookies, RequestsCookieJar)
            assert len(session.cookies) == 0


class TestRequestPreparation:
    """Integration tests for request preparation."""
    
    def test_request_to_prepared_request(self):
        """Test conversion from Request to PreparedRequest."""
        req = Request(
            'POST',
            'http://example.com/api',
            headers={'Content-Type': 'application/json'},
            json={'key': 'value'}
        )
        
        prep = req.prepare()
        
        assert isinstance(prep, PreparedRequest)
        assert prep.method == 'POST'
        assert prep.url == 'http://example.com/api'
        assert 'Content-Type' in prep.headers
        assert prep.body == b'{"key": "value"}'
    
    def test_session_prepares_request_with_auth(self):
        """Test session prepares request with authentication."""
        from requests.auth import HTTPBasicAuth
        
        session = Session()
        session.auth = HTTPBasicAuth('user', 'pass')
        
        req = Request('GET', 'http://example.com')
        prep = session.prepare_request(req)
        
        assert 'Authorization' in prep.headers
        assert prep.headers['Authorization'].startswith('Basic ')


class TestResponseHandling:
    """Integration tests for response handling."""
    
    def test_response_json_parsing(self):
        """Test response JSON parsing."""
        response = Response()
        response._content = b'{"name": "test", "value": 123}'
        response._content_consumed = True
        response.encoding = 'utf-8'
        
        data = response.json()
        
        assert data['name'] == 'test'
        assert data['value'] == 123
    
    def test_response_text_decoding(self):
        """Test response text decoding."""
        response = Response()
        response._content = 'Hello World'.encode('utf-8')
        response._content_consumed = True
        response.encoding = 'utf-8'
        
        text = response.text
        
        assert text == 'Hello World'
    
    def test_response_raises_for_status(self):
        """Test response.raise_for_status()."""
        from requests.exceptions import HTTPError
        
        response = Response()
        response.status_code = 404
        response.url = 'http://example.com'
        response.reason = 'Not Found'
        
        with pytest.raises(HTTPError):
            response.raise_for_status()


class TestCookieHandling:
    """Integration tests for cookie handling."""
    
    def test_cookies_from_dict_to_jar(self):
        """Test converting dict to cookie jar."""
        from requests.cookies import cookiejar_from_dict
        
        cookie_dict = {'session': 'abc123', 'user': 'testuser'}
        jar = cookiejar_from_dict(cookie_dict)
        
        assert jar.get('session') == 'abc123'
        assert jar.get('user') == 'testuser'
    
    def test_session_merges_request_cookies(self):
        """Test session merges request cookies."""
        session = Session()
        session.cookies.set('session_cookie', 'session_value')
        
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b''
        mock_response._content_consumed = True
        
        with patch.object(HTTPAdapter, 'send', return_value=mock_response) as mock_send:
            session.get('http://example.com', cookies={'request_cookie': 'request_value'})
            
            sent_request = mock_send.call_args[0][0]
            assert sent_request._cookies.get('session_cookie') == 'session_value'
            assert sent_request._cookies.get('request_cookie') == 'request_value'


class TestHeaderHandling:
    """Integration tests for header handling."""
    
    def test_case_insensitive_headers(self):
        """Test case-insensitive header access."""
        response = Response()
        response.headers = CaseInsensitiveDict({
            'Content-Type': 'application/json',
            'X-Custom-Header': 'value'
        })
        
        assert response.headers['content-type'] == 'application/json'
        assert response.headers['CONTENT-TYPE'] == 'application/json'
        assert response.headers['x-custom-header'] == 'value'
    
    def test_session_default_headers_included(self):
        """Test session includes default headers."""
        session = Session()
        
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b''
        mock_response._content_consumed = True
        
        with patch.object(HTTPAdapter, 'send', return_value=mock_response) as mock_send:
            session.get('http://example.com')
            
            sent_request = mock_send.call_args[0][0]
            assert 'User-Agent' in sent_request.headers
            assert 'Accept-Encoding' in sent_request.headers


class TestURLHandling:
    """Integration tests for URL handling."""
    
    def test_url_with_params(self):
        """Test URL construction with params."""
        req = PreparedRequest()
        req.prepare_url('http://example.com', {'key': 'value', 'foo': 'bar'})
        
        assert 'key=value' in req.url
        assert 'foo=bar' in req.url
        assert req.url.startswith('http://example.com')
    
    def test_url_encoding(self):
        """Test URL parameter encoding."""
        req = PreparedRequest()
        req.prepare_url('http://example.com', {'key': 'value with spaces'})
        
        assert 'value+with+spaces' in req.url or 'value%20with%20spaces' in req.url


class TestAuthenticationFlow:
    """Integration tests for authentication."""
    
    def test_basic_auth_adds_header(self):
        """Test basic auth adds Authorization header."""
        from requests.auth import HTTPBasicAuth
        
        auth = HTTPBasicAuth('user', 'pass')
        req = PreparedRequest()
        req.headers = CaseInsensitiveDict()
        
        auth(req)
        
        assert 'Authorization' in req.headers
        assert req.headers['Authorization'].startswith('Basic ')
    
    def test_session_applies_auth_to_request(self):
        """Test session applies auth to requests."""
        from requests.auth import HTTPBasicAuth
        
        session = Session()
        session.auth = HTTPBasicAuth('user', 'pass')
        
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b''
        mock_response._content_consumed = True
        
        with patch.object(HTTPAdapter, 'send', return_value=mock_response) as mock_send:
            session.get('http://example.com')
            
            sent_request = mock_send.call_args[0][0]
            assert 'Authorization' in sent_request.headers
