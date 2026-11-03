"""
Key Derivation Functions (KDF) for Hashium.

Provides standard RFC-compliant key derivation primitives:
- HKDF: HMAC-based Extract-and-Expand Key Derivation Function (RFC 5869)
- Scrypt: Memory-hard Password-based Key Derivation Function (RFC 7914)
- HMAC-HCA: Sponge-based Message Authentication Code using the HCA permutation
"""

import hashlib
import hmac
import math
import os
from typing import Optional, Union


def hkdf_extract(salt: Optional[bytes], ikm: bytes, hash_name: str = "sha256") -> bytes:
    """
    HKDF Extract stage (RFC 5869 Step 1): Extract a pseudorandom key (PRK) from IKM.

    PRK = HMAC-Hash(salt, IKM)
    If salt is not provided, it defaults to a string of HashLen zeros.
    """
    hash_func = getattr(hashlib, hash_name)
    hash_len = hash_func().digest_size
    if salt is None or len(salt) == 0:
        salt = b"\x00" * hash_len
    return hmac.new(salt, ikm, hash_func).digest()


def hkdf_expand(prk: bytes, info: bytes, length: int, hash_name: str = "sha256") -> bytes:
    """
    HKDF Expand stage (RFC 5869 Step 2): Expand PRK to desired key length (OKM).

    OKM = T(1) || T(2) || ... || T(N)
    where:
    T(0) = empty string
    T(i) = HMAC-Hash(PRK, T(i-1) || info || byte(i))
    """
    hash_func = getattr(hashlib, hash_name)
    hash_len = hash_func().digest_size
    n = math.ceil(length / hash_len)
    if n > 255:
        raise ValueError(f"Cannot expand to {length} bytes; exceeds 255 * hash_len ({255 * hash_len})")

    t = b""
    okm = bytearray()
    for i in range(1, n + 1):
        t = hmac.new(prk, t + info + bytes([i]), hash_func).digest()
        okm.extend(t)

    return bytes(okm[:length])


def hkdf(
    ikm: Union[str, bytes],
    length: int = 32,
    salt: Optional[Union[str, bytes]] = None,
    info: Union[str, bytes] = b"",
    hash_name: str = "sha256",
) -> bytes:
    """
    Complete HKDF key derivation (Extract + Expand) per RFC 5869.

    Parameters:
        ikm: Input Keying Material (secret password, seed, or pre-shared key).
        length: Number of bytes of output key material to derive.
        salt: Optional salt. If None, a zero-filled salt is used per RFC.
        info: Context and application specific information (can be empty).
        hash_name: Hash algorithm name (e.g. 'sha256', 'sha512', 'sha384').

    Returns:
        Derived key bytes.
    """
    ikm_bytes = ikm.encode("utf-8") if isinstance(ikm, str) else bytes(ikm)
    salt_bytes = (
        salt.encode("utf-8")
        if isinstance(salt, str)
        else (bytes(salt) if salt is not None else None)
    )
    info_bytes = info.encode("utf-8") if isinstance(info, str) else bytes(info)

    prk = hkdf_extract(salt_bytes, ikm_bytes, hash_name=hash_name)
    return hkdf_expand(prk, info_bytes, length, hash_name=hash_name)


def scrypt_kdf(
    password: Union[str, bytes],
    salt: Optional[Union[str, bytes]] = None,
    length: int = 32,
    n: int = 16384,
    r: int = 8,
    p: int = 1,
    maxmem: int = 32 * 1024 * 1024,
) -> bytes:
    """
    Derive keys using Scrypt memory-hard key derivation function (RFC 7914).

    Parameters:
        password: Plaintext password string or bytes.
        salt: Optional salt. If None, 16 random bytes are generated.
        length: Length of derived key in bytes.
        n: CPU/memory cost parameter (must be power of 2, default 16384).
        r: Block size parameter (default 8).
        p: Parallelization parameter (default 1).
        maxmem: Memory limit in bytes (default 32 MB).

    Returns:
        Derived key bytes.
    """
    pw_bytes = password.encode("utf-8") if isinstance(password, str) else bytes(password)
    salt_bytes = (
        salt.encode("utf-8")
        if isinstance(salt, str)
        else (bytes(salt) if salt is not None else os.urandom(16))
    )

    return hashlib.scrypt(
        pw_bytes,
        salt=salt_bytes,
        n=n,
        r=r,
        p=p,
        maxmem=maxmem,
        dklen=length,
    )


def hmac_hca(
    key: Union[str, bytes],
    data: Union[str, bytes],
    output_bits: int = 256,
) -> bytes:
    """
    Compute a keyed Message Authentication Code powered by HCA sponge permutation.
    Domain-separated using "HCAMACTAG:" envelope.
    """
    from hashium.experimental.hca import hca

    k_bytes = key.encode("utf-8") if isinstance(key, str) else bytes(key)
    d_bytes = data.encode("utf-8") if isinstance(data, str) else bytes(data)

    mac_input = (
        b"HCAMAC:"
        + (len(k_bytes)).to_bytes(8, "big")
        + k_bytes
        + (len(d_bytes)).to_bytes(8, "big")
        + d_bytes
    )
    return hca(mac_input, output_bits=output_bits)
