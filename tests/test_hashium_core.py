"""
Regression test suite for Hashium core cryptographic features.
Ensures that all preexisting features (SHA-256, Argon2, PBKDF2, HMAC, AES-256, RSA)
remain completely functional without any regression.
"""

import os
import pytest
from hashium.core import Hashium


@pytest.fixture
def h():
    return Hashium()


def test_basic_sha256(h):
    res = h.hashium_basic("password123")
    assert isinstance(res, str)
    assert len(res) == 64
    assert res == "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"


def test_salted_sha256(h):
    res = h.hashium_salted("password123")
    parts = res.split(":")
    assert len(parts) == 2
    assert len(parts[0]) == 32  # 16 bytes hex salt
    assert len(parts[1]) == 64  # sha256 hex


def test_pbkdf2_roundtrip(h):
    pw = "SecretPBKDF2Password"
    stored = h.hashium_pbkdf2(pw)
    assert h.verify_pbkdf2(pw, stored) is True
    assert h.verify_pbkdf2("WrongPassword", stored) is False


def test_hmac_sha256(h):
    res = h.hashium_hmac("mykey", "mydata")
    assert isinstance(res, str)
    assert len(res) == 64


def test_argon2_roundtrip(h):
    pw = "Argon2SecretPassword"
    hashed = h.hashium_argon2(pw)
    assert h.verify_argon2(pw, hashed) is True
    assert h.verify_argon2("WrongPassword", hashed) is False


def test_aes256_encryption_decryption(h):
    secret = "TopSecretAESMessage"
    encrypted = h.encrypt_data(secret)
    decrypted = h.decrypt_data(encrypted)
    assert decrypted == secret

    # Test with custom key
    custom_key = "my_custom_secret_passphrase_321"
    h_custom = Hashium(aes_key=custom_key)
    enc_custom = h_custom.encrypt_data(secret)
    dec_custom = h_custom.decrypt_data(enc_custom)
    assert dec_custom == secret

    # Test explicit per-call key parameter
    explicit_key = os.urandom(32)
    enc_explicit = h.encrypt_data(secret, key=explicit_key)
    dec_explicit = h.decrypt_data(enc_explicit, key=explicit_key)
    assert dec_explicit == secret


def test_rsa_keygen_sign_verify(h):
    priv, pub = h.generate_rsa_keys(key_size=2048)
    message = "DigitalSignatureVerificationMessage"
    sig = h.sign_data(message, priv)
    assert h.verify_signature(message, sig, pub) is True
    assert h.verify_signature("TamperedMessage", sig, pub) is False


def test_ultra_secure_hash(h):
    pw = "UltraSecurePassword2026"
    res = h.hashium_ultra_secure(pw)
    parts = res.split(":")
    assert len(parts) == 2
    assert len(parts[0]) == 64  # 32 bytes hex salt
    assert len(parts[1]) == 128  # sha512 hex


def test_file_hashing(h, tmp_path):
    demo_file = tmp_path / "test_file.txt"
    demo_file.write_bytes(b"File integrity check test.")
    digest = h.hash_file(str(demo_file))
    assert isinstance(digest, str)
    assert len(digest) == 64
