"""
Test configuration and setup for NinetyDegreeRotator plugin
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_IMAGE_FORMATS = ['JPEG', 'PNG', 'GIF', 'BMP']
TEST_ENCRYPTION_METHODS = ['mautrix', 'manual', 'none']

# Mock data for testing
MOCK_JWK_KEY = {
    "alg": "A256CTR",
    "ext": True,
    "k": "test_key_base64_encoded_32_bytes_exactly",
    "key_ops": ["decrypt"],
    "kty": "oct"
}

MOCK_ENCRYPTED_FILE = {
    "url": "mxc://example.com/test_file",
    "key": MOCK_JWK_KEY,
    "iv": "test_iv_base64_encoded_16_bytes",
    "hashes": {
        "sha256": "test_hash_base64_encoded"
    }
}
