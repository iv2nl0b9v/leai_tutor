"""
Tests for canvas image_data bytes serialization fix.

This test suite verifies that the fix for the ipywidgets bytes_from_json
function works correctly. The original function expected objects with a
.tobytes() method (like memoryview), but in some cases it receives plain
bytes objects, causing an AttributeError.

The fix in app.py patches both the function and the bytes_serialization
dictionary to handle both cases.
"""
import pytest
import ipywidgets.widgets.trait_types as trait_types


# Apply the fix (same as in app.py)
def patched_bytes_from_json(js, obj):
    """Fixed bytes_from_json that handles both bytes and memoryview"""
    if js is None:
        return None
    if isinstance(js, bytes):
        return js
    return js.tobytes()


# Patch both the function and the serialization dictionary
trait_types.bytes_from_json = patched_bytes_from_json
trait_types.bytes_serialization['from_json'] = patched_bytes_from_json


class TestBytesFromJsonFix:
    """Test the bytes_from_json fix handles various input types"""
    
    def test_plain_bytes(self):
        """Test that bytes_from_json handles plain bytes correctly"""
        # This is the case that was failing before the fix
        test_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        result = trait_types.bytes_from_json(test_bytes, None)
        
        assert result == test_bytes
        assert isinstance(result, bytes)
    
    def test_memoryview(self):
        """Test that bytes_from_json still handles memoryview correctly"""
        # This is the original expected case
        test_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        test_memoryview = memoryview(test_bytes)
        
        result = trait_types.bytes_from_json(test_memoryview, None)
        
        assert result == test_bytes
        assert isinstance(result, bytes)
    
    def test_none_value(self):
        """Test that bytes_from_json handles None correctly"""
        result = trait_types.bytes_from_json(None, None)
        assert result is None
    
    def test_bytes_serialization_dict(self):
        """Test that the bytes_serialization dict is properly patched"""
        from ipywidgets.widgets.trait_types import bytes_serialization
        
        # Verify the patch is applied
        assert 'from_json' in bytes_serialization
        
        # Test with plain bytes (the bug case)
        test_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        from_json = bytes_serialization['from_json']
        result = from_json(test_bytes, None)
        
        assert result == test_bytes
        assert isinstance(result, bytes)

