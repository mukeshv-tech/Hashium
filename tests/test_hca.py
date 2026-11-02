"""
Comprehensive test suite for HCA-0.1:
- Comparison between pure Python reference and Rust implementation.
- Known-Answer-Test (KAT) vectors.
- Empty input, single-byte, variable lengths, 64-byte boundaries.
- Streaming vs. one-shot consistency.
- Repeated finalization idempotency.
- Copy and reset behavior.
- Invalid types and invalid output sizes.
"""

import pytest
from hashium.experimental.hca import HCAHasher, hca, hca_parallel
from hashium.experimental.hca_reference import HCAReferenceHasher, hca_reference

# Known-Answer Test vectors generated from the authoritative specification
KNOWN_ANSWER_VECTORS = [
    {
        "input": b"",
        "bits": 512,
        "expected": "a71ad8f73d6001418f139dd3332c7d9e63ff4d131d5c80256ebfd7d1a6c9463e873e1e54e5a1dccdb330758e5045a33c2ee27cdefd4aa6444e11c73879bb2cc4",
    },
    {
        "input": b"a",
        "bits": 256,
        "expected": "2524c1d810ebef9e5ce2d6a7a1954a7150ea60dd80094ab3ee23f2490c216109",
    },
    {
        "input": b"Hello Hashium",
        "bits": 512,
        "expected": "4b0fa2fff3b8f98c5d4ccc48610c96387b08addae5561bda9efc5de441dd14088b7efce5287df130f99222004763772cf7a6c93808e0d6f660e7b5ffc65a70dd",
    },
    {
        "input": b"Hello Hashium",
        "bits": 256,
        "expected": "4b0fa2fff3b8f98c5d4ccc48610c96387b08addae5561bda9efc5de441dd1408",
    },
    {
        "input": b"Hello Hashium",
        "bits": 128,
        "expected": "4b0fa2fff3b8f98c5d4ccc48610c9638",
    },
]


@pytest.mark.parametrize("vector", KNOWN_ANSWER_VECTORS)
def test_known_answer_vectors(vector):
    inp = vector["input"]
    bits = vector["bits"]
    expected = vector["expected"]

    # Verify reference implementation
    ref_digest = hca_reference(inp, output_bits=bits).hex()
    assert ref_digest == expected

    # Verify native implementation one-shot
    native_digest = hca(inp, output_bits=bits).hex()
    assert native_digest == expected

    # Verify native hasher streaming
    hasher = HCAHasher(output_bits=bits)
    hasher.update(inp)
    assert hasher.hexdigest() == expected


def test_empty_input():
    d1 = hca(b"", output_bits=512)
    d2 = hca_reference(b"", output_bits=512)
    assert d1 == d2
    assert len(d1) == 64


def test_single_byte_inputs():
    for byte_val in [b"\x00", b"\x01", b"\xff", b"a", b"Z"]:
        native = hca(byte_val, output_bits=256)
        ref = hca_reference(byte_val, output_bits=256)
        assert native == ref


@pytest.mark.parametrize("length", [0, 1, 55, 56, 63, 64, 65, 119, 120, 127, 128, 129, 256, 1024])
def test_boundary_and_variable_lengths(length):
    data = bytes([i % 251 for i in range(length)])
    native = hca(data, output_bits=512)
    ref = hca_reference(data, output_bits=512)
    assert native == ref


def test_utf8_encoded_input():
    text = "Hashium 🚀 密码学 (Cryptographie)"
    data = text.encode("utf-8")
    assert hca(data, output_bits=512) == hca_reference(data, output_bits=512)


@pytest.mark.parametrize("bits", [128, 192, 256, 384, 512, 1024, 2048, 4096])
def test_variable_output_lengths(bits):
    data = b"Arbitrary length test vector for HCA-0.1"
    native = hca(data, output_bits=bits)
    ref = hca_reference(data, output_bits=bits)
    assert len(native) == bits // 8
    assert native == ref


def test_streaming_vs_oneshot():
    data = b"Chunk 1 | " * 50 + b"Chunk 2 | " * 30 + b"Chunk 3 final."
    oneshot = hca(data, output_bits=512)

    hasher = HCAHasher(output_bits=512)
    step = 17
    for i in range(0, len(data), step):
        hasher.update(data[i : i + step])

    assert hasher.digest() == oneshot
    assert hasher.hexdigest() == oneshot.hex()


def test_repeated_finalization_is_idempotent():
    hasher = HCAHasher(output_bits=256)
    hasher.update(b"Repeat test")
    first = hasher.digest()
    second = hasher.digest()
    third = hasher.hexdigest()
    assert first == second
    assert first.hex() == third


def test_copy_and_reset():
    h1 = HCAHasher(output_bits=256)
    h1.update(b"Prefix:")
    h2 = h1.copy()

    h1.update(b"A")
    h2.update(b"B")

    assert h1.digest() != h2.digest()

    h1.reset()
    h1.update(b"Prefix:B")
    assert h1.digest() == h2.digest()


def test_invalid_input_types():
    hasher = HCAHasher(output_bits=256)
    with pytest.raises(TypeError):
        hasher.update("string not bytes")

    with pytest.raises(TypeError):
        hca("string not bytes", 256)

    with pytest.raises(TypeError):
        hasher.update(12345)


def test_invalid_output_sizes():
    with pytest.raises(ValueError):
        HCAHasher(output_bits=64)  # Below 128

    with pytest.raises(ValueError):
        HCAHasher(output_bits=5000)  # Above 4096

    with pytest.raises(ValueError):
        HCAHasher(output_bits=255)  # Not multiple of 8

    with pytest.raises(ValueError):
        hca(b"data", output_bits=100)


def test_bytearray_and_memoryview_supported():
    raw = b"Bytearray and memoryview test"
    ba = bytearray(raw)
    mv = memoryview(raw)

    ref = hca(raw, 256)
    assert hca(ba, 256) == ref
    assert hca(mv, 256) == ref


def test_hca_parallel_small_and_large():
    # Below leaf threshold (<= 16KB), parallel hash matches sequential hash
    data_small = b"Test small payload under 16KB"
    assert hca_parallel(data_small, 512) == hca(data_small, 512)

    # Multi-chunk payload (> 128KB for 64KB chunks)
    data_large = b"Chunked parallel verification payload..." * 4000
    res1 = hca_parallel(data_large, 512)
    res2 = hca_parallel(data_large, 512)
    assert len(res1) == 64
    assert res1 == res2
    assert res1 != hca(data_large, 512)  # Tree hashing intentionally separates tree structure
