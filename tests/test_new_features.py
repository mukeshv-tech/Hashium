"""
Comprehensive test suite for newly added Hashium 1.0 features:
- RFC 5869 HKDF test vectors (Extract & Expand)
- RFC 7914 Scrypt KDF functionality
- RFC 8439 ChaCha20-Poly1305 AEAD cipher test vectors & roundtrips
- AES-256-GCM AEAD encryption & tamper detection
- Cryptographic File Shredder (DoD 3-pass, random, and zero wipe)
- Checksum Manifest creation & verification
- HMAC-HCA keyed sponge MAC
"""

import os
import pytest
from hashium import Hashium
from hashium.kdf import hkdf, hkdf_extract, hkdf_expand, scrypt_kdf, hmac_hca
from hashium.ciphers import (
    chacha20_poly1305_encrypt,
    chacha20_poly1305_decrypt,
    aes_gcm_encrypt,
    aes_gcm_decrypt,
)
from hashium.shredder import shred_file


@pytest.fixture
def h():
    return Hashium()


# ==============================================================================
# 1. HKDF Tests (RFC 5869 Test Vector 1 & 2)
# ==============================================================================

def test_rfc5869_test_case_1():
    """RFC 5869 Test Case 1: SHA-256 with standard IKM, salt, info."""
    ikm = bytes.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")
    salt = bytes.fromhex("000102030405060708090a0b0c")
    info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
    length = 42

    prk = hkdf_extract(salt, ikm, hash_name="sha256")
    expected_prk = bytes.fromhex("077709362c2e32df0ddc3f0dc47bba6390b6c73bb50f9c3122ec844ad7c2b3e5")
    assert prk == expected_prk

    okm = hkdf_expand(prk, info, length, hash_name="sha256")
    expected_okm = bytes.fromhex(
        "3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865"
    )
    assert okm == expected_okm

    # One-shot API test
    assert hkdf(ikm, length=length, salt=salt, info=info, hash_name="sha256") == expected_okm


def test_rfc5869_test_case_2():
    """RFC 5869 Test Case 2: Longer IKM and info (80-byte inputs, 82-byte output)."""
    ikm = bytes([i for i in range(80)])
    salt = bytes([i for i in range(96, 96 + 80)])
    info = bytes([i for i in range(176, 176 + 80)])
    length = 82

    okm = hkdf(ikm, length=length, salt=salt, info=info, hash_name="sha256")
    expected_okm = bytes.fromhex(
        "b11e398dc80327a1c8e7f78c596a49344f012eda2d4efad8a050cc4c19afa97c"
        "59045a99cac7827271cb41c65e590e09da3275600c2f09b8367793a9aca3db71"
        "cc30c58179ec3e87c14c01d5c1f3434f1d87"
    )
    assert okm == expected_okm


# ==============================================================================
# 2. Scrypt KDF Tests
# ==============================================================================

def test_scrypt_kdf_basic(h):
    pw = "P@ssw0rdScryptSecure"
    salt = b"SodiumChloride16"
    key1 = scrypt_kdf(pw, salt=salt, length=32, n=1024, r=8, p=1)
    key2 = h.scrypt(pw, salt=salt, length=32, n=1024, r=8, p=1)
    assert len(key1) == 32
    assert key1 == key2

    # Different salt produces distinct keys
    key_other = scrypt_kdf(pw, salt=b"DifferentSalt123", length=32, n=1024, r=8, p=1)
    assert key1 != key_other


# ==============================================================================
# 3. HMAC-HCA Sponge MAC Tests
# ==============================================================================

def test_hmac_hca_deterministic(h):
    key = "secret_mac_key"
    data = "Critical authenticated financial transaction"
    mac1 = hmac_hca(key, data, output_bits=256)
    mac2 = h.hmac_hca(key, data, output_bits=256)
    assert len(mac1) == 32
    assert mac1 == mac2

    # Key sensitivity
    mac_wrong_key = hmac_hca("wrong_key", data, output_bits=256)
    assert mac1 != mac_wrong_key

    # Data sensitivity
    mac_tampered = hmac_hca(key, data + "!", output_bits=256)
    assert mac1 != mac_tampered


# ==============================================================================
# 4. ChaCha20-Poly1305 AEAD Tests (RFC 8439)
# ==============================================================================

def test_rfc8439_chacha20_poly1305_vector():
    """RFC 8439 Section 2.8.2 test vector."""
    key = bytes.fromhex("808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9f")
    nonce = bytes.fromhex("070000004041424344454647")
    ad = bytes.fromhex("50515253c0c1c2c3c4c5c6c7")
    plaintext = b"Ladies and Gentlemen of the class of '99: If I could offer you only one tip for the future, sunscreen would be it."

    n, tag, ct = chacha20_poly1305_encrypt(plaintext, key, nonce=nonce, associated_data=ad)
    assert n == nonce

    # Expected tag from RFC 8439 Section 2.8.2
    expected_tag = bytes.fromhex("1ae10b594f09e26a7e902ecbd0600691")
    assert tag == expected_tag

    # Roundtrip decryption
    decrypted = chacha20_poly1305_decrypt(ct, key, nonce, tag, associated_data=ad)
    assert decrypted == plaintext


def test_chacha20_poly1305_tamper_detection(h):
    key = os.urandom(32)
    nonce, tag, ct = h.chacha20_poly1305_encrypt("Sensitive Confidential Data", key, associated_data="HeaderV1")

    # Valid decrypt
    pt = h.chacha20_poly1305_decrypt(ct, key, nonce, tag, associated_data="HeaderV1")
    assert pt == b"Sensitive Confidential Data"

    # Ciphertext tamper
    tampered_ct = bytearray(ct)
    tampered_ct[0] ^= 0x01
    with pytest.raises(ValueError):
        h.chacha20_poly1305_decrypt(bytes(tampered_ct), key, nonce, tag, associated_data="HeaderV1")

    # Associated data tamper
    with pytest.raises(ValueError):
        h.chacha20_poly1305_decrypt(ct, key, nonce, tag, associated_data="HeaderV2")


# ==============================================================================
# 5. AES-256-GCM AEAD Tests
# ==============================================================================

def test_aes_gcm_roundtrip_and_tamper(h):
    key = os.urandom(32)
    ad = b"ProtocolVersion=2.0"
    plaintext = "AES-GCM Authenticated Payload"

    nonce, tag, ct = h.aes_gcm_encrypt(plaintext, key=key, associated_data=ad)
    assert len(nonce) == 12
    assert len(tag) == 16

    # Clean decryption
    recovered = h.aes_gcm_decrypt(ct, key=key, nonce=nonce, tag=tag, associated_data=ad)
    assert recovered.decode("utf-8") == plaintext

    # Tamper check
    with pytest.raises(ValueError):
        h.aes_gcm_decrypt(ct, key=key, nonce=nonce, tag=tag, associated_data=b"TamperedAD")


# ==============================================================================
# 6. Cryptographic File Shredder Tests
# ==============================================================================

def test_file_shredding_dod(h, tmp_path):
    secret_file = tmp_path / "top_secret.docx"
    content = b"Super confidential military grade data " * 500
    secret_file.write_bytes(content)
    assert os.path.exists(str(secret_file))

    # Shred with DoD 3-pass wipe
    success = h.shred_file(str(secret_file), passes=3, method="dod")
    assert success is True
    assert not os.path.exists(str(secret_file))


def test_file_shredding_random(tmp_path):
    target = tmp_path / "random_wipe.bin"
    target.write_bytes(b"A" * 8192)
    assert shred_file(str(target), passes=1, method="random") is True
    assert not os.path.exists(str(target))


# ==============================================================================
# 7. Checksum CLI Integration Tests
# ==============================================================================

def test_checksum_create_and_verify(tmp_path):
    from hashium.cli import _create_checksums, _verify_checksums
    import argparse

    f1 = tmp_path / "file1.txt"
    f1.write_text("Hello Hashium Checksums 1", encoding="utf-8")
    f2 = tmp_path / "file2.txt"
    f2.write_text("Hello Hashium Checksums 2", encoding="utf-8")

    manifest = tmp_path / "CHECKSUMS.sha256"

    # Create manifest
    create_args = argparse.Namespace(
        targets=[str(f1), str(f2)],
        algo="sha256",
        bits=256,
        out=str(manifest),
    )
    _create_checksums(create_args)
    assert os.path.exists(str(manifest))

    # Verify manifest
    verify_args = argparse.Namespace(
        manifest=str(manifest),
        algo="sha256",
    )
    _verify_checksums(verify_args)  # Should execute without error
