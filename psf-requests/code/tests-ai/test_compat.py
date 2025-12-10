"""
Tests for requests.compat module.
"""
import sys
import pytest

from requests import compat


class TestCompatModule:
    """Tests for compatibility module."""
    
    def test_has_is_py2(self):
        """Should define is_py2."""
        assert hasattr(compat, 'is_py2')
        assert isinstance(compat.is_py2, bool)
    
    def test_has_is_py3(self):
        """Should define is_py3."""
        assert hasattr(compat, 'is_py3')
        assert isinstance(compat.is_py3, bool)
    
    def test_py2_or_py3(self):
        """Either is_py2 or is_py3 should be True."""
        assert compat.is_py2 or compat.is_py3
    
    def test_has_json_module(self):
        """Should have json module."""
        assert hasattr(compat, 'json')
    
    def test_has_urlparse(self):
        """Should have urlparse function."""
        assert hasattr(compat, 'urlparse')
        assert callable(compat.urlparse)
    
    def test_has_urlencode(self):
        """Should have urlencode function."""
        assert hasattr(compat, 'urlencode')
        assert callable(compat.urlencode)
    
    def test_has_quote(self):
        """Should have quote function."""
        assert hasattr(compat, 'quote')
        assert callable(compat.quote)
    
    def test_has_unquote(self):
        """Should have unquote function."""
        assert hasattr(compat, 'unquote')
        assert callable(compat.unquote)
    
    def test_has_str_type(self):
        """Should define str type."""
        assert hasattr(compat, 'str')
    
    def test_has_bytes_type(self):
        """Should define bytes type."""
        assert hasattr(compat, 'bytes')
    
    def test_has_basestring_type(self):
        """Should define basestring."""
        assert hasattr(compat, 'basestring')
    
    def test_urlparse_works(self):
        """urlparse should work correctly."""
        result = compat.urlparse('http://example.com/path?query=value')
        
        assert result.scheme == 'http'
        assert result.netloc == 'example.com'
        assert result.path == '/path'
    
    def test_urlencode_works(self):
        """urlencode should encode params."""
        result = compat.urlencode([('key', 'value'), ('foo', 'bar')])
        
        assert 'key=value' in result
        assert 'foo=bar' in result
    
    def test_quote_works(self):
        """quote should percent-encode strings."""
        result = compat.quote('hello world')
        
        assert 'hello%20world' == result
    
    def test_unquote_works(self):
        """unquote should decode percent-encoded strings."""
        result = compat.unquote('hello%20world')
        
        assert result == 'hello world'


class TestCompatTypes:
    """Tests for type compatibility."""
    
    def test_builtin_str_exists(self):
        """Should define builtin_str."""
        assert hasattr(compat, 'builtin_str')
    
    def test_numeric_types_exists(self):
        """Should define numeric_types."""
        assert hasattr(compat, 'numeric_types')
        assert isinstance(compat.numeric_types, tuple)
    
    def test_integer_types_exists(self):
        """Should define integer_types."""
        assert hasattr(compat, 'integer_types')
        assert isinstance(compat.integer_types, tuple)
