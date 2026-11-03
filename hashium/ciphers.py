"""
Modern Production Authenticated Ciphers (AEAD) for Hashium.

Provides standard RFC and NIST compliant authenticated encryption:
- ChaCha20-Poly1305 (RFC 8439)
- AES-256-GCM (NIST SP 800-38D)
"""

import os
from typing import Optional, Tuple, Union
from Crypto.Cipher import ChaCha20_Poly1305, AES  # nosec B413


def chacha20_poly1305_encrypt(
    plaintext: Union[str, bytes],
    key: Union[str, bytes],
    nonce: Optional[bytes] = None,
    associated_data: Optional[Union[str, bytes]] = None,
) -> Tuple[bytes, bytes, bytes]:
    """
    Encrypt plaintext using ChaCha20-Poly1305 AEAD cipher (RFC 8439).

    Parameters:
        plaintext: Data to encrypt.
        key: 32-byte (256-bit) secret key.
        nonce: Optional 12-byte (96-bit) nonce. Generated randomly if None.
        associated_data: Optional unencrypted metadata to authenticate.

    Returns:
        Tuple of (nonce, tag, ciphertext) as bytes.
    """
    pt_bytes = plaintext.encode("utf-8") if isinstance(plaintext, str) else bytes(plaintext)
    k_bytes = _ensure_key_length(key, 32, "ChaCha20-Poly1305")

    if nonce is None:
        nonce = os.urandom(12)
    elif len(nonce) != 12:
        raise ValueError(f"ChaCha20-Poly1305 nonce must be exactly 12 bytes, got {len(nonce)}")

    cipher = ChaCha20_Poly1305.new(key=k_bytes, nonce=nonce)
    if associated_data:
        ad_bytes = (
            associated_data.encode("utf-8")
            if isinstance(associated_data, str)
            else bytes(associated_data)
        )
        cipher.update(ad_bytes)

    ciphertext, tag = cipher.encrypt_and_digest(pt_bytes)
    return nonce, tag, ciphertext


def chacha20_poly1305_decrypt(
    ciphertext: bytes,
    key: Union[str, bytes],
    nonce: bytes,
    tag: bytes,
    associated_data: Optional[Union[str, bytes]] = None,
) -> bytes:
    """
    Decrypt and verify ciphertext using ChaCha20-Poly1305 AEAD cipher.

    Returns:
        Decrypted plaintext bytes. Raises ValueError if tag is invalid.
    """
    k_bytes = _ensure_key_length(key, 32, "ChaCha20-Poly1305")
    cipher = ChaCha20_Poly1305.new(key=k_bytes, nonce=nonce)

    if associated_data:
        ad_bytes = (
            associated_data.encode("utf-8")
            if isinstance(associated_data, str)
            else bytes(associated_data)
        )
        cipher.update(ad_bytes)

    return cipher.decrypt_and_verify(ciphertext, tag)


def aes_gcm_encrypt(
    plaintext: Union[str, bytes],
    key: Union[str, bytes],
    nonce: Optional[bytes] = None,
    associated_data: Optional[Union[str, bytes]] = None,
) -> Tuple[bytes, bytes, bytes]:
    """
    Encrypt plaintext using AES-256-GCM AEAD cipher (NIST SP 800-38D).

    Parameters:
        plaintext: Data to encrypt.
        key: 16, 24, or 32-byte secret key (256-bit recommended).
        nonce: Optional 12-byte standard GCM nonce. Generated randomly if None.
        associated_data: Optional authenticated metadata.

    Returns:
        Tuple of (nonce, tag, ciphertext) as bytes.
    """
    pt_bytes = plaintext.encode("utf-8") if isinstance(plaintext, str) else bytes(plaintext)
    k_bytes = _ensure_aes_key(key)

    if nonce is None:
        nonce = os.urandom(12)
    elif len(nonce) < 12:
        raise ValueError("AES-GCM nonce should be at least 12 bytes")

    cipher = AES.new(k_bytes, AES.MODE_GCM, nonce=nonce)
    if associated_data:
        ad_bytes = (
            associated_data.encode("utf-8")
            if isinstance(associated_data, str)
            else bytes(associated_data)
        )
        cipher.update(ad_bytes)

    ciphertext, tag = cipher.encrypt_and_digest(pt_bytes)
    return nonce, tag, ciphertext


def aes_gcm_decrypt(
    ciphertext: bytes,
    key: Union[str, bytes],
    nonce: bytes,
    tag: bytes,
    associated_data: Optional[Union[str, bytes]] = None,
) -> bytes:
    """
    Decrypt and verify ciphertext using AES-GCM AEAD cipher.

    Returns:
        Decrypted plaintext bytes. Raises ValueError if tag or ciphertext was tampered with.
    """
    k_bytes = _ensure_aes_key(key)
    cipher = AES.new(k_bytes, AES.MODE_GCM, nonce=nonce)

    if associated_data:
        ad_bytes = (
            associated_data.encode("utf-8")
            if isinstance(associated_data, str)
            else bytes(associated_data)
        )
        cipher.update(ad_bytes)

    return cipher.decrypt_and_verify(ciphertext, tag)


def _ensure_key_length(key: Union[str, bytes], target_len: int, algo_name: str) -> bytes:
    import hashlib
    if isinstance(key, str):
        if len(key) == target_len * 2 and all(c in "0123456789abcdefABCDEF" for c in key):
            return bytes.fromhex(key)
        # Derive via sha256 to ensure exact 32 bytes
        return hashlib.sha256(key.encode("utf-8")).digest()
    k_bytes = bytes(key)
    if len(k_bytes) != target_len:
        raise ValueError(f"{algo_name} key must be exactly {target_len} bytes, got {len(k_bytes)}")
    return k_bytes


def _ensure_aes_key(key: Union[str, bytes]) -> bytes:
    import hashlib
    if isinstance(key, str):
        if len(key) in (32, 48, 64) and all(c in "0123456789abcdefABCDEF" for c in key):
            return bytes.fromhex(key)
        return hashlib.sha256(key.encode("utf-8")).digest()
    k_bytes = bytes(key)
    if len(k_bytes) not in (16, 24, 32):
        raise ValueError(f"AES key must be 16, 24, or 32 bytes, got {len(k_bytes)}")
    return k_bytes
