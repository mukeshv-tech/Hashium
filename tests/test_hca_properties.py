"""
Property-based test suite using Hypothesis for HCA-0.3.
Validates:
- Equivalence between Rust native core and pure Python reference implementation.
- Arbitrary binary inputs and arbitrary chunk boundary streaming.
- Determinism and idempotency of repeated finalization.
- Copy state independence and reset behavior.
- Sponge prefix consistency (shorter outputs are strict prefixes of longer outputs).
"""

import pytest
from hypothesis import given, settings, strategies as st
from hashium.experimental.hca import HCAHasher, hca
from hashium.experimental.hca_reference import HCAReferenceHasher, hca_reference


@given(
    data=st.binary(min_size=0, max_size=2048),
    output_bits=st.sampled_from([128, 192, 256, 384, 512, 1024, 2048]),
)
@settings(max_examples=60, deadline=None)
def test_property_rust_vs_python_reference(data: bytes, output_bits: int):
    """Verify that native Rust core and pure Python reference match for all inputs."""
    native_digest = hca(data, output_bits=output_bits)
    ref_digest = hca_reference(data, output_bits=output_bits)
    assert native_digest == ref_digest
    assert len(native_digest) == output_bits // 8


@given(
    chunks=st.lists(st.binary(min_size=0, max_size=500), min_size=1, max_size=10),
    output_bits=st.sampled_from([256, 512]),
)
@settings(max_examples=50, deadline=None)
def test_property_arbitrary_chunked_streaming(chunks: list, output_bits: int):
    """Verify arbitrary chunk boundary streaming matches one-shot hashing."""
    hasher = HCAHasher(output_bits=output_bits)
    total_data = bytearray()
    for chunk in chunks:
        hasher.update(chunk)
        total_data.extend(chunk)

    stream_digest = hasher.digest()
    oneshot_digest = hca(bytes(total_data), output_bits=output_bits)
    assert stream_digest == oneshot_digest


@given(
    data=st.binary(min_size=0, max_size=1000),
    output_bits=st.sampled_from([256, 512]),
)
@settings(max_examples=40, deadline=None)
def test_property_repeated_digest_idempotency(data: bytes, output_bits: int):
    """Calling digest() multiple times must not alter internal state or result."""
    hasher = HCAHasher(output_bits=output_bits)
    hasher.update(data)

    first = hasher.digest()
    second = hasher.digest()
    third = hasher.hexdigest()

    assert first == second
    assert first.hex() == third


@given(
    prefix=st.binary(min_size=0, max_size=500),
    suffix_a=st.binary(min_size=1, max_size=300),
    suffix_b=st.binary(min_size=1, max_size=300),
)
@settings(max_examples=40, deadline=None)
def test_property_copy_independence(prefix: bytes, suffix_a: bytes, suffix_b: bytes):
    """A copied hasher must diverge independently from the original."""
    h1 = HCAHasher(output_bits=256)
    h1.update(prefix)
    h2 = h1.copy()

    h1.update(suffix_a)
    h2.update(suffix_b)

    d1 = h1.digest()
    d2 = h2.digest()

    if suffix_a != suffix_b:
        assert d1 != d2
    else:
        assert d1 == d2


@given(
    data1=st.binary(min_size=0, max_size=500),
    data2=st.binary(min_size=0, max_size=500),
)
@settings(max_examples=40, deadline=None)
def test_property_reset_behavior(data1: bytes, data2: bytes):
    """Resetting a hasher must return it to identical initial state."""
    h = HCAHasher(output_bits=256)
    h.update(data1)
    h.reset()
    h.update(data2)

    fresh = HCAHasher(output_bits=256)
    fresh.update(data2)

    assert h.digest() == fresh.digest()


@given(
    data=st.binary(min_size=0, max_size=500),
)
@settings(max_examples=30, deadline=None)
def test_property_sponge_output_prefix_consistency(data: bytes):
    """Shorter output lengths must be exact prefixes of longer output lengths."""
    d128 = hca(data, output_bits=128)
    d256 = hca(data, output_bits=256)
    d512 = hca(data, output_bits=512)
    d1024 = hca(data, output_bits=1024)

    assert d256.startswith(d128)
    assert d512.startswith(d256)
    assert d1024.startswith(d512)
