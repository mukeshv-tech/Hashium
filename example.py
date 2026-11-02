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

    print("=" * 70)
    print("             HASHIUM CRYPTOGRAPHY TOOLKIT DEMO")
    print("=" * 70)

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

    # 8. Digital Signature with RSA
    print("\n8. RSA Digital Signature:")
    private_key, public_key = hashium.generate_rsa_keys(key_size=2048)
    signature = hashium.sign_data("secure message", private_key)
    print("   Signature (Base64):", signature[:64] + "...")
    print("   Verify Signature:", hashium.verify_signature("secure message", signature, public_key))

    # 9. Ultra Secure 768+ Bit Hash
    print("\n9. Ultra Secure Hash (768+ bits):")
    print("   Result:", hashium.hashium_ultra_secure("mypassword"))

    # 10. Experimental HCA-0.2 (Hashium Custom Algorithm)
    print("\n" + "=" * 70)
    print("      EXPERIMENTAL: HCA-0.2 (Hashium Custom Algorithm)")
    print("=" * 70)
    print("   [!] Research prototype: Not for production security use.")

    # 10a. Step-by-Step Output Bit Progression (Variable Digest Lengths)
    print("\n10a. HCA-0.2 Variable Output Length (Increasing Step-by-Step):")
    msg = b"Hashium variable output demonstrator"
    bit_steps = [128, 192, 256, 384, 512, 1024, 2048]
    for bits in bit_steps:
        digest = hca(msg, output_bits=bits)
        hex_preview = digest.hex()[:32] + "..." + digest.hex()[-16:] if len(digest.hex()) > 48 else digest.hex()
        print(f"   -> {bits:4d} bits ({bits // 8:3d} bytes): {hex_preview}")

    # 10b. Step-by-Step Message Length Progression (Boundary & Size Scaling)
    print("\n10b. HCA-0.2 Input Length Progression (Across 64-byte Block Boundaries):")
    byte_steps = [0, 1, 16, 55, 56, 63, 64, 65, 127, 128, 129, 256, 1024]
    for size in byte_steps:
        sample_input = b"X" * size
        d = hca(sample_input, output_bits=256)
        blocks = (size + 1 + 8 + 63) // 64
        print(f"   -> Input: {size:4d} bytes | Absorption Blocks: {blocks:2d} | Digest: {d.hex()[:32]}...")

    # 10c. Incremental Streaming Hasher
    print("\n10c. HCA-0.2 Streaming Hasher (chunked update):")
    hasher = HCAHasher(output_bits=256)
    chunks = [b"Hello ", b"Hashium ", b"HCA-0.2 ", b"Incremental ", b"Stream!"]
    cumulative = b""
    for idx, chunk in enumerate(chunks, 1):
        hasher.update(chunk)
        cumulative += chunk
        current_digest = hasher.hexdigest()
        print(f"   Step {idx}: +{len(chunk)} bytes (Total: {len(cumulative):2d} B) -> {current_digest[:32]}...")

    # 10d. Step-by-Step Payload Encryption & Decryption
    print("\n10d. HCA-0.2 Stream Cipher Encryption (Payload Scaling Step-by-Step):")
    key = "MySecureKey-2026"
    test_messages = [
        "Hi",                                              # 2 bytes
        "Short secret phrase",                             # 19 bytes
        "Medium length message designed for cipher demo",  # 46 bytes
        "A" * 64,                                          # Exactly 64 bytes (1 block)
        "Large secret payload: " + ("0123456789ABCDEF" * 8) # 150 bytes
    ]

    for item in test_messages:
        item_bytes_len = len(item.encode("utf-8"))
        encrypted = hca_encrypt(item, key)
        decrypted = hca_decrypt(encrypted, key)
        nonce_hex, cipher_hex = encrypted.split(":")
        print(f"   -> Size: {item_bytes_len:3d} B | Ciphertext: {cipher_hex[:24]}... | Decrypted Match: {decrypted == item}")

    print("\n" + "=" * 70)
    print("                     ALL DEMOS COMPLETED")
    print("=" * 70)

    # Keep console open if run interactively
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
