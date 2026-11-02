import os
import sys

# Ensure local hashium package is resolvable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from hashium import Hashium
from hashium.experimental.hca import (
    HCAHasher,
    hca,
    hca_salted,
    hca_verify_salted,
    hca_encrypt,
    hca_decrypt,
    hca_aead_encrypt,
    hca_aead_decrypt,
)


def main():
    hashium = Hashium()

    print("=" * 80)
    print("           HASHIUM CRYPTOGRAPHY TOOLKIT — OPTIMIZED & AEAD DEMO")
    print("=" * 80)

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

    # 6. AES-256 Encryption/Decryption
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

    # 8. Digital Signature with RSA-4096
    print("\n8. RSA-4096 Digital Signature:")
    private_key, public_key = hashium.generate_rsa_keys(key_size=4096)
    signature = hashium.sign_data("secure message", private_key)
    print("   Signature (Base64):", signature[:64] + "...")
    print("   Verify Signature:", hashium.verify_signature("secure message", signature, public_key))

    # 9. Ultra Secure 768+ Bit Hash
    print("\n9. Ultra Secure Hash (768+ bits):")
    print("   Result:", hashium.hashium_ultra_secure("mypassword"))

    # 10. Experimental HCA-0.2 (Hashium Custom Algorithm)
    print("\n" + "=" * 80)
    print("    EXPERIMENTAL: HCA-0.2 (SIMD-Optimized Sponge Hashing & AEAD)")
    print("=" * 80)
    print("   [!] Research prototype: Not for production security use.")

    # 10a. Variable Output Lengths (Max 4096 bits)
    print("\n10a. HCA-0.2 Variable Output Progression (128 bits -> 4096 bits):")
    msg = b"Hashium Maximum Sponge Extraction Vector"
    all_bit_steps = [128, 256, 512, 1024, 2048, 4096]
    for bits in all_bit_steps:
        d = hca(msg, output_bits=bits)
        print(f"   -> {bits:4d} bits ({bits // 8:3d} bytes): {d.hex()[:32]}...{d.hex()[-16:]}")

    # 10b. Salted Hashing & Verification (Rainbow Table Defense)
    print("\n10b. HCA-0.2 Salted Hashing & Constant-Time Verification:")
    user_pw = "MukeshSuperSecretPassword2026!"
    stored_hash = hca_salted(user_pw, output_bits=256)
    salt_hex, hash_hex = stored_hash.split(":")
    print(f"   Password: {user_pw}")
    print(f"   Generated Salt: {salt_hex} (16 bytes random)")
    print(f"   Salted Hash:    {hash_hex[:32]}... ({len(hash_hex) * 4} bits)")
    print(f"   Verify Match (Correct PW): {hca_verify_salted(user_pw, stored_hash, output_bits=256)}")
    print(f"   Verify Match (Wrong PW):   {hca_verify_salted('WrongPassword', stored_hash, output_bits=256)}")

    # 10c. Streaming & Block Boundaries
    print("\n10b. HCA-0.2 Input Length Progression (0 Bytes -> 100,000 Bytes):")
    large_steps = [0, 64, 512, 4096, 65536, 100000]
    for size in large_steps:
        data = b"\xAA" * size
        h = hca(data, output_bits=512)
        blocks = (size + 1 + 8 + 63) // 64
        print(f"   -> Input: {size:6d} bytes ({size/1024:6.2f} KB) | Absorption Blocks: {blocks:5d} | Digest: {h.hex()[:32]}...")

    # 10c. Stream Cipher Mode
    print("\n10c. HCA-0.2 Stream Cipher (Basic XOR Mode):")
    key = "UltraSecretMasterKey9999"
    plaintext = "Stream cipher demonstration message!"
    enc_stream = hca_encrypt(plaintext, key)
    dec_stream = hca_decrypt(enc_stream, key)
    print(f"   Encrypted (<nonce>:<ciphertext>): {enc_stream[:48]}...")
    print(f"   Decrypted: {dec_stream}")
    print(f"   Match: {dec_stream == plaintext}")

    # 10d. AEAD Authenticated Encryption Mode (Option 2)
    print("\n10d. HCA-0.2 Authenticated Encryption with Associated Data (AEAD Mode):")
    associated_metadata = "PacketHeader:v2.0,ChannelID:994,UserID:Mukesh"
    confidential_data = "AUTHENTICATED FINANCIAL OR HIGHLY SENSITIVE TRANSACTION"

    print(f"   Plaintext: {confidential_data}")
    print(f"   Associated Data (Unencrypted Header): {associated_metadata}")

    # Encrypt with AEAD
    aead_payload = hca_aead_encrypt(confidential_data, key, associated_data=associated_metadata)
    nonce_hex, tag_hex, cipher_hex = aead_payload.split(":")
    print(f"\n   [+] AEAD Payload: <nonce>:<256-bit tag>:<ciphertext>")
    print(f"       Nonce:      {nonce_hex}")
    print(f"       Auth Tag:   {tag_hex}")
    print(f"       Ciphertext: {cipher_hex}")

    # Legitimate Decryption
    decrypted_valid = hca_aead_decrypt(aead_payload, key, associated_data=associated_metadata)
    print(f"\n   [+] Verification & Decryption: SUCCESS")
    print(f"       Recovered Text: {decrypted_valid}")

    # Tamper Simulation Test
    print(f"\n   [+] Tamper Attack Simulation:")
    tampered_payload = f"{nonce_hex}:{tag_hex}:{cipher_hex[:-2]}00"
    try:
        hca_aead_decrypt(tampered_payload, key, associated_data=associated_metadata)
        print("       [!] ERROR: Tamper was NOT caught!")
    except Exception as e:
        print(f"       [PASS] ATTACK BLOCKED: {e}")

    # Header Modification Simulation
    try:
        hca_aead_decrypt(aead_payload, key, associated_data="PacketHeader:v2.0,ChannelID:666,UserID:Attacker")
        print("       [!] ERROR: Header forgery was NOT caught!")
    except Exception as e:
        print(f"       [PASS] FORGERY BLOCKED: {e}")

    print("\n" + "=" * 80)
    print("                     ALL DEMOS COMPLETED")
    print("=" * 80)

    # Keep console open if run interactively
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
