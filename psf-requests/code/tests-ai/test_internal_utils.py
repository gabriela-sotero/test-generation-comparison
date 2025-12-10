"""
Tests for requests._internal_utils module.
"""
import pytest

from requests._internal_utils import to_native_string, unicode_is_ascii


class TestToNativeString:
    """Tests for to_native_string() function."""
    
    def test_returns_string_unchanged(self):
        """Should return string unchanged."""
        result = to_native_string('test string')
        
        assert result == 'test string'
        assert isinstance(result, str)
    
    def test_converts_bytes_to_string(self):
        """Should convert bytes to string."""
        result = to_native_string(b'test bytes')
        
        assert result == 'test bytes'
        assert isinstance(result, str)
    
    def test_uses_specified_encoding(self):
        """Should use specified encoding."""
        data = 'café'.encode('utf-8')
        
        result = to_native_string(data, encoding='utf-8')
        
        assert result == 'café'
    
    def test_handles_ascii_by_default(self):
        """Should default to ASCII encoding."""
        result = to_native_string(b'ascii')
        
        assert result == 'ascii'


class TestUnicodeIsAscii:
    """Tests for unicode_is_ascii() function."""
    
    def test_returns_true_for_ascii(self):
        """Should return True for ASCII strings."""
        result = unicode_is_ascii('hello world')
        
        assert result is True
    
    def test_returns_false_for_non_ascii(self):
        """Should return False for non-ASCII strings."""
        result = unicode_is_ascii('café')
        
        assert result is False
    
    def test_returns_true_for_empty_string(self):
        """Should return True for empty string."""
        result = unicode_is_ascii('')
        
        assert result is True
    
    def test_returns_true_for_ascii_numbers(self):
        """Should return True for numeric strings."""
        result = unicode_is_ascii('12345')
        
        assert result is True
    
    def test_returns_true_for_ascii_symbols(self):
        """Should return True for ASCII symbols."""
        result = unicode_is_ascii('!@#$%^&*()')
        
        assert result is True
    
    def test_returns_false_for_emoji(self):
        """Should return False for emoji."""
        result = unicode_is_ascii('hello 👋')
        
        assert result is False
