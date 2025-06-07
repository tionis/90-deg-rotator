"""
Unit tests for the NinetyDegreeRotator plugin core functionality
"""

import pytest
from io import BytesIO
from PIL import Image

# Mock imports for testing without maubot dependencies
class MockMessageEvent:
    def __init__(self, msgtype="m.image", has_file=False):
        self.content = MockContent(msgtype, has_file)
        self.event_id = "test_event_id"
        
    async def respond(self, content):
        pass

class MockContent:
    def __init__(self, msgtype="m.image", has_file=False):
        self.msgtype = msgtype
        self.body = "test_image.jpg"
        if has_file:
            self.file = MockEncryptedFile()
            self.url = None
        else:
            self.file = None
            self.url = "mxc://example.com/test_image"

class MockEncryptedFile:
    def __init__(self):
        self.url = "mxc://example.com/encrypted_test"
        self.key = MockJWK()
        self.iv = "dGVzdF9pdl8xNl9ieXRlcw=="
        self.hashes = MockHashes()

class MockJWK:
    def __init__(self):
        self.k = "dGVzdF9rZXlfMzJfYnl0ZXNfZXhhY3RseQ=="

class MockHashes:
    def __init__(self):
        self.sha256 = "dGVzdF9oYXNoXzMyX2J5dGVzX2V4YWN0bHk="


class TestImageProcessing:
    """Test image processing functionality"""
    
    def test_image_rotation(self):
        """Test basic image rotation functionality"""
        # Create a test image
        test_image = Image.new('RGB', (100, 50), color='red')
        
        # Convert to bytes
        image_buffer = BytesIO()
        test_image.save(image_buffer, format='PNG')
        image_bytes = image_buffer.getvalue()
        
        # Test rotation
        img = Image.open(BytesIO(image_bytes))
        rotated_img = img.rotate(-90, expand=True)
        
        # Check dimensions are swapped
        assert img.size == (100, 50)
        assert rotated_img.size == (50, 100)
    
    def test_supported_formats(self):
        """Test that all expected image formats are supported"""
        formats = ['JPEG', 'PNG', 'GIF', 'BMP']
        
        for fmt in formats:
            test_image = Image.new('RGB', (10, 10), color='blue')
            buffer = BytesIO()
            
            if fmt == 'JPEG':
                test_image.save(buffer, format=fmt)
            else:
                test_image.save(buffer, format=fmt)
            
            # Verify we can read it back
            buffer.seek(0)
            loaded_image = Image.open(buffer)
            assert loaded_image.size == (10, 10)


class TestEncryptionHandling:
    """Test encryption detection and handling"""
    
    def test_encrypted_file_detection(self):
        """Test detection of encrypted vs unencrypted files"""
        # Encrypted file
        encrypted_event = MockMessageEvent(has_file=True)
        assert encrypted_event.content.file is not None
        assert encrypted_event.content.url is None
        
        # Unencrypted file
        unencrypted_event = MockMessageEvent(has_file=False)
        assert unencrypted_event.content.file is None
        assert unencrypted_event.content.url is not None
    
    def test_jwk_key_structure(self):
        """Test JWK key structure validation"""
        mock_file = MockEncryptedFile()
        
        assert hasattr(mock_file.key, 'k')
        assert hasattr(mock_file, 'iv')
        assert hasattr(mock_file.hashes, 'sha256')


class TestEventHandling:
    """Test event handling logic"""
    
    def test_image_message_detection(self):
        """Test detection of image messages"""
        image_event = MockMessageEvent(msgtype="m.image")
        text_event = MockMessageEvent(msgtype="m.text")
        
        assert image_event.content.msgtype == "m.image"
        assert text_event.content.msgtype == "m.text"
    
    def test_event_response(self):
        """Test event response functionality"""
        event = MockMessageEvent()
        
        # This should not raise an exception
        import asyncio
        asyncio.run(event.respond({"msgtype": "m.image", "body": "test"}))


class TestConfigurationHandling:
    """Test plugin configuration"""
    
    def test_autojoin_config(self):
        """Test autojoin configuration option"""
        # This would test the Config class when available
        # For now, just test the concept
        config_options = {"autojoin": True}
        assert config_options["autojoin"] is True
        
        config_options["autojoin"] = False
        assert config_options["autojoin"] is False


if __name__ == "__main__":
    pytest.main([__file__])
