"""
HCA-0.1: Hashium Custom Algorithm Python Interface.

Provides HCAHasher and hca under the hashium.experimental.hca namespace.
Backed by the native Rust _hca_core extension.
"""

from typing import Union
import _hca_core

# Re-export native class
HCAHasher = _hca_core.HCAHasher


def hca(data: Union[bytes, bytearray, memoryview], output_bits: int = 512) -> bytes:
    """
    Compute HCA-0.1 hash of input data.

    Parameters:
        data: bytes-like object to hash.
        output_bits: length of output digest in bits (128 to 4096, multiple of 8).

    Returns:
        Digest bytes.
    """
    return _hca_core.hca(data, output_bits)


__all__ = ["HCAHasher", "hca"]
