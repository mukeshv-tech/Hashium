"""
HCA-0.2: Hashium Custom Algorithm Python Interface.

Provides:
- HCAHasher and hca (Hashing)
- hca_encrypt and hca_decrypt (Symmetric Stream Encryption/Decryption)
under the hashium.experimental.hca namespace.
Backed by the native Rust _hca_core extension.
"""

import os
from typing import Union
import _hca_core

# Re-export native class
HCAHasher = _hca_core.HCAHasher


def hca(data: Union[bytes, bytearray, memoryview], output_bits: int = 512) -> bytes:
    """
    Compute HCA-0.2 hash of input data.

    Parameters:
        data: bytes-like object to hash.
        output_bits: length of output digest in bits (128 to 4096, multiple of 8).

    Returns:
        Digest bytes.
    """
    return _hca_core.hca(data, output_bits)


def hca_encrypt(data: Union[str, bytes], key: Union[str, bytes], nonce: bytes = None) -> str:
    """
    Encrypt data using HCA-0.2 as a symmetric stream cipher keystream generator.

    Format: <nonce_hex>:<ciphertext_hex>

    Parameters:
        data: Plaintext string or bytes.
        key: Secret encryption key (string or bytes).
        nonce: Optional 16-byte nonce. If not provided, a secure random nonce is generated.

    Returns:
        Colon-separated string: '<nonce_hex>:<ciphertext_hex>'
    """
    data_bytes = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    key_bytes = key.encode("utf-8") if isinstance(key, str) else bytes(key)

    if nonce is None:
        nonce = os.urandom(16)
    else:
        nonce = bytes(nonce)

    ciphertext = _hca_core.hca_cipher_process(data_bytes, key_bytes, nonce)
    return f"{nonce.hex()}:{ciphertext.hex()}"


def hca_decrypt(encrypted_payload: str, key: Union[str, bytes]) -> str:
    """
    Decrypt an HCA-0.2 encrypted payload (<nonce_hex>:<ciphertext_hex>).

    Parameters:
        encrypted_payload: String in '<nonce_hex>:<ciphertext_hex>' format.
        key: Secret encryption key matching the one used for encryption.

    Returns:
        Decrypted plaintext as a decoded UTF-8 string.
    """
    key_bytes = key.encode("utf-8") if isinstance(key, str) else bytes(key)
    parts = encrypted_payload.split(":")
    if len(parts) != 2:
        raise ValueError("Invalid encrypted payload format, expected '<nonce_hex>:<ciphertext_hex>'")

    nonce = bytes.fromhex(parts[0])
    ciphertext = bytes.fromhex(parts[1])

    plaintext_bytes = _hca_core.hca_cipher_process(ciphertext, key_bytes, nonce)
    return plaintext_bytes.decode("utf-8")


def hca_decrypt_raw(encrypted_payload: str, key: Union[str, bytes]) -> bytes:
    """
    Decrypt an HCA-0.2 encrypted payload to raw bytes.
    """
    key_bytes = key.encode("utf-8") if isinstance(key, str) else bytes(key)
    parts = encrypted_payload.split(":")
    if len(parts) != 2:
        raise ValueError("Invalid encrypted payload format, expected '<nonce_hex>:<ciphertext_hex>'")

    nonce = bytes.fromhex(parts[0])
    ciphertext = bytes.fromhex(parts[1])

    return _hca_core.hca_cipher_process(ciphertext, key_bytes, nonce)


__all__ = ["HCAHasher", "hca", "hca_encrypt", "hca_decrypt", "hca_decrypt_raw"]
