"""
HCA-0.2: Hashium Custom Algorithm Python Interface.

Provides:
- HCAHasher and hca (Hashing)
- hca_encrypt and hca_decrypt (Symmetric Stream Encryption/Decryption)
- hca_aead_encrypt and hca_aead_decrypt (Authenticated Encryption with Associated Data)
under the hashium.experimental.hca namespace.
Backed by the native Rust _hca_core extension.
"""

import os
from typing import Union, Tuple, Optional
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


def hca_parallel(data: Union[bytes, bytearray, memoryview], output_bits: int = 512) -> bytes:
    """
    Compute HCA tree hash utilizing multi-core parallel processing (via Rayon).
    Releases the Python GIL during parallel tree execution.

    Parameters:
        data: bytes-like object to hash.
        output_bits: length of output digest in bits (128 to 4096, multiple of 8).

    Returns:
        Digest bytes.
    """
    return _hca_core.hca_parallel(data, output_bits)


def hca_salted(
    data: Union[str, bytes],
    salt: Optional[Union[str, bytes]] = None,
    output_bits: int = 512,
    salt_bytes_len: int = 16,
) -> str:
    """
    Compute a salted HCA-0.2 hash.

    Format: '<salt_hex>:<hash_hex>'

    Parameters:
        data: Plaintext password or data string/bytes.
        salt: Optional specific salt. If None, a cryptographically secure random salt is generated.
        output_bits: Output bit length (128 to 4096, default 512).
        salt_bytes_len: Length of random salt in bytes (default 16).

    Returns:
        Formatted string: '<salt_hex>:<hash_hex>'
    """
    data_bytes = data.encode("utf-8") if isinstance(data, str) else bytes(data)

    if salt is None:
        salt_b = os.urandom(salt_bytes_len)
    elif isinstance(salt, str):
        salt_b = bytes.fromhex(salt) if len(salt) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in salt) else salt.encode("utf-8")
    else:
        salt_b = bytes(salt)

    # Domain-separated salted absorption: "HCASALT:" || salt || ":" || data
    salted_input = b"HCASALT:" + salt_b + b":" + data_bytes
    digest = _hca_core.hca(salted_input, output_bits)
    return f"{salt_b.hex()}:{digest.hex()}"


def hca_verify_salted(
    data: Union[str, bytes],
    stored_salted_hash: str,
    output_bits: int = 512,
) -> bool:
    """
    Verify a plaintext data against a stored salted HCA-0.2 hash string (<salt_hex>:<hash_hex>).

    Uses constant-time comparison to prevent timing attacks.
    """
    import hmac

    parts = stored_salted_hash.split(":")
    if len(parts) != 2:
        return False

    salt_hex, expected_hash_hex = parts[0], parts[1]
    calculated = hca_salted(data, salt=salt_hex, output_bits=output_bits)
    _, calculated_hash_hex = calculated.split(":")

    return hmac.compare_digest(expected_hash_hex, calculated_hash_hex)


def hca_encrypt(data: Union[str, bytes], key: Union[str, bytes], nonce: Optional[bytes] = None) -> str:
    """
    Encrypt data using HCA-0.2 as a symmetric stream cipher keystream generator.

    Format: <nonce_hex>:<ciphertext_hex>

    Parameters:
        data: Plaintext string or bytes.
        key: Secret encryption key (string or bytes).
        nonce: Optional 16-byte nonce. If not provided, a random nonce is generated.

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


def hca_aead_encrypt(
    plaintext: Union[str, bytes],
    key: Union[str, bytes],
    associated_data: Optional[Union[str, bytes]] = b"",
    nonce: Optional[bytes] = None,
) -> str:
    """
    AEAD Authenticated Encryption: Encrypts plaintext and generates a 256-bit authentication tag
    binding the associated data and ciphertext together.

    Format: <nonce_hex>:<tag_hex>:<ciphertext_hex>

    Parameters:
        plaintext: Plaintext string or bytes.
        key: Secret key string or bytes.
        associated_data: Authenticated, unencrypted metadata (e.g. headers, protocol ID).
        nonce: Optional 16-byte nonce.

    Returns:
        Colon-separated string: '<nonce_hex>:<tag_hex>:<ciphertext_hex>'
    """
    pt_bytes = plaintext.encode("utf-8") if isinstance(plaintext, str) else bytes(plaintext)
    key_bytes = key.encode("utf-8") if isinstance(key, str) else bytes(key)
    ad_bytes = (
        associated_data.encode("utf-8")
        if isinstance(associated_data, str)
        else bytes(associated_data or b"")
    )

    if nonce is None:
        nonce = os.urandom(16)
    else:
        nonce = bytes(nonce)

    ciphertext, tag = _hca_core.hca_aead_encrypt(pt_bytes, key_bytes, nonce, ad_bytes)
    return f"{nonce.hex()}:{tag.hex()}:{ciphertext.hex()}"


def hca_aead_decrypt(
    encrypted_payload: str,
    key: Union[str, bytes],
    associated_data: Optional[Union[str, bytes]] = b"",
) -> str:
    """
    AEAD Authenticated Decryption: Verifies tag in constant time before decryption.
    Fails if the ciphertext or associated data has been tampered with.

    Parameters:
        encrypted_payload: '<nonce_hex>:<tag_hex>:<ciphertext_hex>'
        key: Secret key string or bytes.
        associated_data: Authenticated metadata matching encryption.

    Returns:
        Decrypted plaintext as a decoded UTF-8 string.
    """
    key_bytes = key.encode("utf-8") if isinstance(key, str) else bytes(key)
    ad_bytes = (
        associated_data.encode("utf-8")
        if isinstance(associated_data, str)
        else bytes(associated_data or b"")
    )

    parts = encrypted_payload.split(":")
    if len(parts) != 3:
        raise ValueError("Invalid AEAD payload format, expected '<nonce_hex>:<tag_hex>:<ciphertext_hex>'")

    nonce = bytes.fromhex(parts[0])
    tag = bytes.fromhex(parts[1])
    ciphertext = bytes.fromhex(parts[2])

    plaintext_bytes = _hca_core.hca_aead_decrypt(ciphertext, key_bytes, nonce, tag, ad_bytes)
    return plaintext_bytes.decode("utf-8")


__all__ = [
    "HCAHasher",
    "hca",
    "hca_parallel",
    "hca_salted",
    "hca_verify_salted",
    "hca_encrypt",
    "hca_decrypt",
    "hca_aead_encrypt",
    "hca_aead_decrypt",
]
