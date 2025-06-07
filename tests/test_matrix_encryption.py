#!/usr/bin/env python3
"""
Test script to understand Matrix file encryption format
"""

import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def test_matrix_file_decryption():
    """
    Matrix file encryption uses AES-CTR with:
    - JWK (JSON Web Key) format for the key
    - Base64-encoded IV
    - SHA256 hash verification
    
    The file structure should be:
    {
        "url": "mxc://...",
        "key": {
            "alg": "A256CTR",
            "ext": true,
            "k": "base64-encoded-key",
            "key_ops": ["decrypt"],
            "kty": "oct"
        },
        "iv": "base64-encoded-iv",
        "hashes": {
            "sha256": "base64-encoded-hash"
        }
    }
    """
    print("Matrix file encryption format:")
    print("1. Key is in JWK format with 'k' field containing base64 key")
    print("2. IV is base64 encoded")
    print("3. Algorithm is AES-CTR")
    print("4. Hash verification using SHA256")
    
    # Example of how to extract and use the key/iv
    print("\nExtraction process:")
    print("key_data = base64.b64decode(file_info.key.k)")
    print("iv_data = base64.b64decode(file_info.iv)")
    print("cipher = Cipher(algorithms.AES(key_data), modes.CTR(iv_data))")

if __name__ == "__main__":
    test_matrix_file_decryption()
