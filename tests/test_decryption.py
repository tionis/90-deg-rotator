#!/usr/bin/env python3
"""
Test the Matrix file decryption logic
"""

import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from PIL import Image
from io import BytesIO

def test_decryption_logic():
    """Test the Matrix file decryption implementation"""
    print("Testing Matrix file decryption logic...")
    
    # Test base64 padding function
    def add_base64_padding(s):
        return s + '=' * (4 - len(s) % 4) if len(s) % 4 else s
    
    # Test cases
    test_cases = [
        "YWJjZA",  # "abcd" without padding
        "YWJjZA==",  # "abcd" with padding
        "YWJj",  # "abc" without padding
        "YWJj=",  # "abc" with padding
    ]
    
    for test in test_cases:
        try:
            padded = add_base64_padding(test)
            decoded = base64.b64decode(padded)
            print(f"✓ '{test}' -> '{padded}' -> {decoded}")
        except Exception as e:
            print(f"✗ '{test}' failed: {e}")
    
    # Test AES-CTR decryption with known values
    print("\nTesting AES-CTR decryption...")
    try:
        # Generate test key and IV
        key = b'0123456789abcdef' * 2  # 32 bytes for AES-256
        iv = b'0123456789abcdef'  # 16 bytes for AES
        
        # Test data
        test_data = b"Hello, Matrix file encryption!"
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(test_data) + encryptor.finalize()
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        
        if decrypted == test_data:
            print("✓ AES-CTR encryption/decryption working correctly")
        else:
            print("✗ AES-CTR test failed")
            
    except Exception as e:
        print(f"✗ AES-CTR test error: {e}")

if __name__ == "__main__":
    test_decryption_logic()
