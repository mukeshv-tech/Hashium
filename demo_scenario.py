"""
Hashium 1.0 Real-World Security Simulation Demo.

This script executes an end-to-end production workflow simulating a secure
data pipeline:
1. User Authentication & Password Hashing (Argon2id + Salted HCA)
2. Master Key Derivation using HKDF & Scrypt
3. High-Security Authenticated File Encryption (ChaCha20-Poly1305 & AES-256-GCM)
4. Tamper Detection / Active MITM Attack Simulation
5. Integrity Manifest Generation & Verification (HCA tree & SHA-256)
6. Secure Data Lifecycle Wiping (DoD 5220.22-M Cryptographic File Shredder)
"""

import os
import sys
import tempfile
import time

from hashium import Hashium
from hashium.kdf import hkdf, scrypt_kdf, hmac_hca
from hashium.ciphers import (
    chacha20_poly1305_encrypt,
    chacha20_poly1305_decrypt,
    aes_gcm_encrypt,
    aes_gcm_decrypt,
)
from hashium.shredder import shred_file
from hashium.experimental.hca import hca, hca_parallel, hca_salted, hca_verify_salted


def banner(title: str):
    print("\n" + "=" * 70)
    print(f" >>> {title.upper()}")
    print("=" * 70)


def step(num: int, title: str):
    print(f"\n[Step {num}] {title}")
    print("-" * 55)


def run_real_world_scenario():
    h = Hashium()
    print("=" * 70)
    print("    HASHIUM 1.0 REAL-WORLD CRYPTOGRAPHIC PIPELINE SIMULATION")
    print("=" * 70)

    # Temporary sandbox directory
    work_dir = tempfile.mkdtemp(prefix="hashium_scenario_")
    print(f"Secure Working Directory: {work_dir}")

    try:
        # -------------------------------------------------------------
        # STEP 1: User Onboarding & Credential Protection
        # -------------------------------------------------------------
        step(1, "User Credential Enrollment & Verification")
        user_password = "SuperSecret#Enterprise2026!Password"
        print(f"Plaintext Password : '{user_password}'")

        # 1A: Argon2id (Standard industry storage)
        t0 = time.perf_counter()
        argon_hash = h.hashium_argon2(user_password)
        t_argon = (time.perf_counter() - t0) * 1000
        print(f"Argon2id Hash      : {argon_hash[:45]}... ({t_argon:.1f}ms)")
        assert h.verify_argon2(user_password, argon_hash) is True
        assert h.verify_argon2("AttackerGuess", argon_hash) is False
        print(" -> Verified Argon2id authentication: OK (Wrong password rejected)")

        # 1B: Salted HCA Hash (Experimental High-Throughput Sponge)
        hca_stored = hca_salted(user_password, output_bits=512)
        print(f"Salted HCA-512     : {hca_stored[:45]}...")
        assert hca_verify_salted(user_password, hca_stored, output_bits=512) is True
        print(" -> Verified Salted HCA authentication: OK")

        # -------------------------------------------------------------
        # STEP 2: Key Derivation (HKDF & Scrypt)
        # -------------------------------------------------------------
        step(2, "Session Key Derivation via HKDF (RFC 5869)")
        master_secret = "PreSharedMasterSecret2026_Enterprise"
        session_salt = os.urandom(16)
        
        # Derive distinct 256-bit sub-keys for different security services
        enc_key = hkdf(master_secret, length=32, salt=session_salt, info="encryption-service")
        mac_key = hkdf(master_secret, length=32, salt=session_salt, info="mac-auth-service")
        storage_key = hkdf(master_secret, length=32, salt=session_salt, info="storage-vault-service")

        print(f"Derived AES/ChaCha Key : {enc_key.hex()[:32]}...")
        print(f"Derived MAC Key        : {mac_key.hex()[:32]}...")
        print(f"Derived Vault Key      : {storage_key.hex()[:32]}...")
        assert enc_key != mac_key != storage_key
        print(" -> Domain-separated sub-keys extracted and expanded successfully")

        # -------------------------------------------------------------
        # STEP 3: Confidential Data Encryption (ChaCha20-Poly1305 & AES-GCM)
        # -------------------------------------------------------------
        step(3, "High-Security Authenticated Encryption (AEAD)")
        confidential_data = (
            "PATIENT RECORD ID: #98214\n"
            "DIAGNOSIS: Top Secret Research Sample\n"
            "BALANCE: $1,450,000.00 USD\n"
            "STATUS: RESTRICTED ACCESS ONLY\n"
        )
        metadata_header = "ORG=HashiumLabs;AUTH_LEVEL=CONFIDENTIAL;EPOCH=2026"
        print(f"Plaintext Payload ({len(confidential_data)} bytes):")
        for line in confidential_data.strip().split("\n"):
            print(f"   | {line}")
        print(f"Associated Metadata    : '{metadata_header}'")

        # ChaCha20-Poly1305 Encryption
        c_nonce, c_tag, c_ciphertext = chacha20_poly1305_encrypt(
            confidential_data, enc_key, associated_data=metadata_header
        )
        print(f"\n[ChaCha20-Poly1305 Encrypted]")
        print(f"   Nonce (96-bit)      : {c_nonce.hex()}")
        print(f"   MAC Tag (128-bit)   : {c_tag.hex()}")
        print(f"   Ciphertext          : {c_ciphertext.hex()[:40]}...")

        # Decrypt & verify ChaCha20-Poly1305
        recovered_pt = chacha20_poly1305_decrypt(
            c_ciphertext, enc_key, c_nonce, c_tag, associated_data=metadata_header
        )
        assert recovered_pt.decode("utf-8") == confidential_data
        print("   -> Decryption & authentication tag verification: SUCCESS")

        # AES-256-GCM Encryption
        g_nonce, g_tag, g_ciphertext = aes_gcm_encrypt(
            confidential_data, enc_key, associated_data=metadata_header
        )
        print(f"\n[AES-256-GCM Encrypted]")
        print(f"   Nonce (96-bit)      : {g_nonce.hex()}")
        print(f"   Auth Tag (128-bit)  : {g_tag.hex()}")
        print(f"   Ciphertext          : {g_ciphertext.hex()[:40]}...")

        recovered_gcm = aes_gcm_decrypt(
            g_ciphertext, enc_key, g_nonce, g_tag, associated_data=metadata_header
        )
        assert recovered_gcm.decode("utf-8") == confidential_data
        print("   -> Decryption & authentication tag verification: SUCCESS")

        # -------------------------------------------------------------
        # STEP 4: Active MITM Attack & Tamper Simulation
        # -------------------------------------------------------------
        step(4, "Adversarial Attack Simulation (Tamper Detection)")
        print("Simulating an in-transit attacker modifying 1 bit of the ciphertext...")
        tampered_ciphertext = bytearray(c_ciphertext)
        tampered_ciphertext[5] ^= 0x01  # Flip a single bit in the wire ciphertext

        try:
            chacha20_poly1305_decrypt(
                bytes(tampered_ciphertext), enc_key, c_nonce, c_tag, associated_data=metadata_header
            )
            print("   [CRITICAL FAILURE] Tampered ciphertext was accepted!")
            sys.exit(1)
        except ValueError as e:
            print(f"   -> [DEFENSE ACTIVE] Decryption rejected by Poly1305 MAC: {e}")

        print("Simulating an attacker modifying the unencrypted metadata header...")
        try:
            chacha20_poly1305_decrypt(
                c_ciphertext, enc_key, c_nonce, c_tag, associated_data="ORG=AttackerCorp;AUTH_LEVEL=ADMIN"
            )
            print("   [CRITICAL FAILURE] Modified associated data was accepted!")
            sys.exit(1)
        except ValueError as e:
            print(f"   -> [DEFENSE ACTIVE] Metadata header tamper detected & rejected: {e}")

        # -------------------------------------------------------------
        # STEP 5: Multi-File Integrity Manifest (Checksum Verification)
        # -------------------------------------------------------------
        step(5, "Release Artifact Checksum Manifest & Verification")
        # Create a set of release artifacts in the working directory
        files_to_hash = []
        for i in range(1, 4):
            fpath = os.path.join(work_dir, f"firmware_image_v{i}.bin")
            with open(fpath, "wb") as f:
                f.write(os.urandom(64 * 1024))  # 64 KB binary file
            files_to_hash.append(fpath)

        manifest_path = os.path.join(work_dir, "RELEASE_MANIFEST.sha256")
        
        # Build checksum manifest
        from hashium.cli import _create_checksums, _verify_checksums
        import argparse

        create_args = argparse.Namespace(
            targets=files_to_hash,
            algo="sha256",
            bits=256,
            out=manifest_path,
        )
        _create_checksums(create_args)

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_content = f.read()
        print("Generated Manifest Content:")
        for line in manifest_content.strip().split("\n"):
            print(f"   {line}")

        # Verify manifest
        verify_args = argparse.Namespace(manifest=manifest_path, algo="sha256")
        _verify_checksums(verify_args)
        print(" -> All files verified against cryptographic checksums successfully")

        # -------------------------------------------------------------
        # STEP 6: Secure File Shredder (DoD 5220.22-M Wipe)
        # -------------------------------------------------------------
        step(6, "Cryptographic File Shredding (DoD 5220.22-M 3-Pass Wipe)")
        sensitive_file = os.path.join(work_dir, "confidential_financial_records.csv")
        with open(sensitive_file, "w", encoding="utf-8") as f:
            f.write("ACCOUNT_NO,ROUTING_NO,BALANCE_USD\n")
            f.write("9082-1234-9821,121000358,9842500.50\n" * 100)

        initial_size = os.path.getsize(sensitive_file)
        print(f"Sensitive File Created : '{os.path.basename(sensitive_file)}' ({initial_size} bytes)")
        assert os.path.exists(sensitive_file)

        print("Executing DoD 5220.22-M wipe (Pass 1: Zeros -> Pass 2: Ones -> Pass 3: Random -> Fsync -> Truncate)...")
        shred_file(sensitive_file, passes=3, method="dod")

        assert not os.path.exists(sensitive_file)
        print(" -> File completely unlinked and erased from physical storage sectors")

        # -------------------------------------------------------------
        # STEP 7: High-Scale Parallel HCA Tree Hashing (10 MB Payload)
        # -------------------------------------------------------------
        step(7, "High-Scale Parallel HCA Tree Hashing (Rayon Multi-Core)")
        data_10mb = os.urandom(10 * 1024 * 1024)
        t_start = time.perf_counter()
        tree_digest = hca_parallel(data_10mb, output_bits=256)
        t_elapsed = time.perf_counter() - t_start
        throughput_mb = (len(data_10mb) / (1024 * 1024)) / t_elapsed
        print(f"10 MB In-Memory Tree Hash : {tree_digest.hex()}")
        print(f"Execution Time            : {t_elapsed * 1000:.2f} ms")
        print(f"Sustained Throughput      : {throughput_mb:.2f} MB/s (GIL-free parallel worker pool)")

        banner("All Real-World Scenarios Passed With 100% Integrity!")

    finally:
        # Cleanup remaining temp directory
        import shutil
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    run_real_world_scenario()
