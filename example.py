import os
import sys

# Ensure local hashium package is resolvable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from hashium import Hashium
from hashium.experimental.hca import (
    HCAHasher,
    hca,
    hca_encrypt,
    hca_decrypt,
)


def main():
    hashium = Hashium()

    print("=" * 75)
    print("             HASHIUM CRYPTOGRAPHY TOOLKIT — MAXIMUM EXTENT DEMO")
    print("=" * 75)

    # 1. Basic SHA-256 Hash
    print("\n1. Basic SHA-256 Hash:")
    print("   Result:", hashium.hashium_basic("mypassword"))

    # 2. Salted SHA-256 Hash
    print("\n2. Salted SHA-256 Hash:")
    print("   Result:", hashium.hashium_salted("mypassword"))

    # 3. PBKDF2 Hashing and Verification
    print("\n3. PBKDF2 Hash:")
    pbkdf2_hash = hashium.hashium_pbkdf2("mypassword")
    print("   Result:", pbkdf2_hash)
    print("   Verify PBKDF2:", hashium.verify_pbkdf2("mypassword", pbkdf2_hash))

    # 4. HMAC Hash
    print("\n4. HMAC-SHA256 Hash:")
    print("   Result:", hashium.hashium_hmac("mysecretkey", "mypassword"))

    # 5. Argon2 Hashing and Verification
    print("\n5. Argon2 Hash:")
    argon_hash = hashium.hashium_argon2("mypassword")
    print("   Result:", argon_hash)
    print("   Verify Argon2:", hashium.verify_argon2("mypassword", argon_hash))

    # 6. AES Encryption/Decryption
    print("\n6. AES-256 Encryption and Decryption:")
    encrypted = hashium.encrypt_data("mypassword")
    print("   Encrypted:", encrypted)
    print("   Decrypted:", hashium.decrypt_data(encrypted))

    # 7. File Hashing (demo.txt)
    print("\n7. File Hash (demo.txt):")
    demo_created = False
    if not os.path.exists("demo.txt"):
        with open("demo.txt", "w", encoding="utf-8") as f:
            f.write("Hashium file integrity test vector.")
        demo_created = True

    try:
        print("   File SHA-256:", hashium.hash_file("demo.txt"))
    finally:
        if demo_created and os.path.exists("demo.txt"):
            os.remove("demo.txt")

    # 8. Digital Signature with RSA-4096 (Max RSA standard)
    print("\n8. RSA-4096 Digital Signature (Maximum Security Parameter):")
    private_key, public_key = hashium.generate_rsa_keys(key_size=4096)
    signature = hashium.sign_data("secure message", private_key)
    print("   Signature (Base64):", signature[:64] + "...")
    print("   Verify Signature:", hashium.verify_signature("secure message", signature, public_key))

    # 9. Ultra Secure 768+ Bit Hash
    print("\n9. Ultra Secure Hash (768+ bits):")
    print("   Result:", hashium.hashium_ultra_secure("mypassword"))

    # 10. Experimental HCA-0.2 Max Capacity & Max Scale Demonstrator
    print("\n" + "=" * 75)
    print("    EXPERIMENTAL: HCA-0.2 — MAXIMUM SPECIFICATION PARAMETERS (4096 BITS)")
    print("=" * 75)
    print("   [!] Research prototype: Not for production security use.")

    # 10a. Full Progression to the Theoretical Maximum Output Size (4096 bits / 512 bytes)
    print("\n10a. HCA-0.2 Variable Output Progression (Max Specification: 4096 Bits):")
    msg = b"Hashium Maximum Sponge Extraction Vector"
    all_bit_steps = [128, 256, 512, 1024, 2048, 3072, 4096]
    for bits in all_bit_steps:
        d = hca(msg, output_bits=bits)
        print(f"   -> {bits:4d} bits ({bits // 8:3d} bytes) [Hex length: {len(d.hex()):4d}]: {d.hex()[:28]}...{d.hex()[-16:]}")

    # Full display of the maximum 4096-bit digest
    max_digest = hca(msg, output_bits=4096)
    print("\n   [+] Complete 4096-Bit (512-Byte) Giant Digest (1024 hex chars):")
    hex_str = max_digest.hex()
    for row in range(0, len(hex_str), 128):
        print(f"       {hex_str[row:row+128]}")

    # 10b. Max Incremental Input Stress (Large Payload Stream)
    print("\n10b. HCA-0.2 Max Input Progression (0 Bytes -> 100,000 Bytes):")
    large_steps = [0, 64, 512, 4096, 16384, 65536, 100000]
    for size in large_steps:
        data = b"\xAA" * size
        h = hca(data, output_bits=512)
        blocks = (size + 1 + 8 + 63) // 64
        print(f"   -> Input: {size:6d} bytes ({size/1024:6.2f} KB) | Absorption Blocks: {blocks:5d} | Digest: {h.hex()[:32]}...")

    # 10c. Stream Cipher Encryption at Maximum Payload
    print("\n10c. HCA-0.2 Stream Cipher — Max Payload Encryption & Decryption:")
    key = "UltraSecretMasterKey9999"
    # Large payload of 10,000 bytes
    large_plaintext = "CONFIDENTIAL_PAYLOAD_DATA_" * 400  # 10,400 bytes
    print(f"   Encrypting {len(large_plaintext):,d} byte payload with HCA keystream...")
    
    enc = hca_encrypt(large_plaintext, key)
    nonce_hex, cipher_hex = enc.split(":")
    print(f"   Nonce:      {nonce_hex}")
    print(f"   Ciphertext: {cipher_hex[:48]}... ({len(cipher_hex) // 2:,d} bytes)")

    dec = hca_decrypt(enc, key)
    print(f"   Decrypted Match: {dec == large_plaintext} (Length: {len(dec):,d} bytes)")

    print("\n" + "=" * 75)
    print("                     MAXIMUM DEMO COMPLETED")
    print("=" * 75)

    # Keep console open if run interactively
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
