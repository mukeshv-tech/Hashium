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

    print("=" * 65)
    print("           HASHIUM CRYPTOGRAPHY TOOLKIT DEMO")
    print("=" * 65)

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
    print("\n" + "=" * 65)
    print("    EXPERIMENTAL: HCA-0.2 (Hashium Custom Algorithm)")
    print("=" * 65)
    print("   [!] Research prototype: Not for production security use.")

    # 10a. One-shot variable output lengths
    data = b"Hello Hashium HCA-0.2"
    hca_256 = hca(data, output_bits=256)
    hca_512 = hca(data, output_bits=512)
    print(f"\n10a. HCA-0.2 One-Shot Digest (Input: {data!r}):")
    print("   256-bit Digest (hex):", hca_256.hex())
    print("   512-bit Digest (hex):", hca_512.hex())

    # 10b. Streaming hasher
    print("\n10b. HCA-0.2 Streaming Hasher (chunked update):")
    hasher = HCAHasher(output_bits=256)
    hasher.update(b"Hello ")
    hasher.update(b"Hashium ")
    hasher.update(b"HCA-0.2")
    stream_digest = hasher.hexdigest()
    print("   Streamed Result (hex):", stream_digest)
    print("   Matches One-Shot:", stream_digest == hca_256.hex())

    # Hasher copy and branch
    branch_hasher = hasher.copy()
    hasher.update(b" [Stream A]")
    branch_hasher.update(b" [Stream B]")
    print(f"   Forked Stream A:", hasher.hexdigest())
    print(f"   Forked Stream B:", branch_hasher.hexdigest())

    # 10c. HCA-0.2 Symmetric Stream Encryption & Decryption
    print("\n10c. HCA-0.2 Encryption & Decryption (Stream Cipher Mode):")
    secret_key = "MySuperSecretPasswordKey!"
    secret_message = "Confidential message protected by native HCA-0.2 sponge cipher!"
    print(f"   Original Plaintext: {secret_message}")

    # Encrypt
    hca_encrypted = hca_encrypt(secret_message, secret_key)
    print(f"   Encrypted (<nonce>:<ciphertext>): {hca_encrypted}")

    # Decrypt
    hca_decrypted = hca_decrypt(hca_encrypted, secret_key)
    print(f"   Decrypted Plaintext: {hca_decrypted}")
    print(f"   Successful Decryption Match: {secret_message == hca_decrypted}")

    print("\n" + "=" * 65)
    print("                  ALL DEMOS COMPLETED")
    print("=" * 65)

    # Keep console open if run interactively
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
