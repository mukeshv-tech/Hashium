"""
Hashium Command-Line Interface (CLI).

Provides terminal commands for:
- One-shot and streaming hashing (SHA-256, HCA-0.2)
- HCA-0.2 Symmetric Stream & AEAD Encryption/Decryption
- File integrity hashing
- Performance benchmarking
"""

import argparse
import sys
import os

# Ensure local package resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hashium.core import Hashium
from hashium.experimental.hca import (
    hca,
    HCAHasher,
    hca_salted,
    hca_verify_salted,
    hca_encrypt,
    hca_decrypt,
    hca_aead_encrypt,
    hca_aead_decrypt,
)


def cmd_hash(args):
    """Hash string data or a file."""
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: '{args.file}'", file=sys.stderr)
            sys.exit(1)
        if args.algo == "hca":
            if args.salted:
                # Read file for salted hashing
                with open(args.file, "rb") as f:
                    data = f.read()
                print(hca_salted(data, output_bits=args.bits))
            else:
                hasher = HCAHasher(output_bits=args.bits)
                with open(args.file, "rb") as f:
                    while chunk := f.read(65536):
                        hasher.update(chunk)
                print(hasher.hexdigest())
            return
        elif args.algo == "sha256":
            h = Hashium()
            if args.salted:
                with open(args.file, "rb") as f:
                    data = f.read()
                print(h.hashium_salted(data.decode("utf-8", errors="replace")))
            else:
                print(h.hash_file(args.file))
            return
    elif args.text is not None:
        data = args.text.encode("utf-8")
    else:
        # Read from stdin if piped
        if not sys.stdin.isatty():
            data = sys.stdin.buffer.read()
        else:
            print("Error: Provide text (-t), file (-f), or pipe standard input.", file=sys.stderr)
            sys.exit(1)

    if args.algo == "hca":
        if args.salted:
            print(hca_salted(data, output_bits=args.bits))
        else:
            digest = hca(data, output_bits=args.bits)
            print(digest.hex())
    elif args.algo == "sha256":
        h = Hashium()
        if args.salted:
            print(h.hashium_salted(data.decode("utf-8", errors="replace")))
        elif args.file:
            print(h.hash_file(args.file))
        else:
            import hashlib
            print(hashlib.sha256(data).hexdigest())


def cmd_encrypt(args):
    """Encrypt a string or file."""
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: '{args.file}'", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "rb") as f:
            plaintext = f.read()
    elif args.text is not None:
        plaintext = args.text
    else:
        print("Error: Provide plaintext text (-t) or file (-f).", file=sys.stderr)
        sys.exit(1)

    if args.aead:
        ad = args.ad or ""
        payload = hca_aead_encrypt(plaintext, args.key, associated_data=ad)
    else:
        payload = hca_encrypt(plaintext, args.key)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(payload)
        print(f"[OK] Encrypted payload written to '{args.out}'")
    else:
        print(payload)


def cmd_decrypt(args):
    """Decrypt an encrypted payload."""
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: '{args.file}'", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            payload = f.read().strip()
    elif args.payload:
        payload = args.payload
    elif args.payload_pos:
        payload = args.payload_pos
    elif not sys.stdin.isatty():
        # Read payload piped via standard input
        payload = sys.stdin.read().strip()
    else:
        # Prompt interactively if not provided as argument or piped
        try:
            payload = input("Enter encrypted payload (<nonce>:<ciphertext>): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.", file=sys.stderr)
            sys.exit(1)

    if not payload:
        print("Error: Empty payload provided.", file=sys.stderr)
        sys.exit(1)

    key = args.key
    if not key:
        if sys.stdin.isatty():
            import getpass
            try:
                key = getpass.getpass("Enter secret key: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nAborted.", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error reading key: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            try:
                key = sys.stdin.readline().strip()
            except (EOFError, KeyboardInterrupt):
                key = ""

    if not key:
        print("Error: Secret key cannot be empty.", file=sys.stderr)
        sys.exit(1)

    try:
        parts = payload.split(":")
        if len(parts) == 3:  # AEAD format: nonce:tag:ciphertext
            ad = args.ad or ""
            plaintext = hca_aead_decrypt(payload, key, associated_data=ad)
        elif len(parts) == 2:  # Stream format: nonce:ciphertext
            plaintext = hca_decrypt(payload, key)
        else:
            print("Error: Unrecognized payload format. Must be <nonce>:<ciphertext> or <nonce>:<tag>:<ciphertext>", file=sys.stderr)
            sys.exit(1)

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(plaintext)
            print(f"[OK] Decrypted plaintext written to '{args.out}'")
        else:
            print(plaintext)
    except Exception as e:
        print(f"Decryption failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_benchmark(args):
    """Run built-in performance benchmarks."""
    from benchmarks.benchmark_hca import run_benchmark
    run_benchmark()


def cmd_shred(args):
    """Securely overwrite and shred a file."""
    from hashium.shredder import shred_file
    for target in args.files:
        try:
            shred_file(target, passes=args.passes, method=args.method)
            print(f"[OK] Securely shredded '{target}' ({args.passes} passes, method: {args.method})")
        except Exception as e:
            print(f"[ERROR] Failed to shred '{target}': {e}", file=sys.stderr)


def cmd_kdf(args):
    """Derive keys via HKDF or Scrypt."""
    from hashium.kdf import hkdf, scrypt_kdf
    password = args.password
    salt = args.salt or ""
    length = args.length

    if args.type == "hkdf":
        info = args.info or ""
        derived = hkdf(password, length=length, salt=salt, info=info, hash_name=args.hash)
    elif args.type == "scrypt":
        derived = scrypt_kdf(password, salt=salt, length=length, n=args.cost_n, r=args.block_r, p=args.parallel_p)
    else:
        print(f"Error: Unknown KDF type '{args.type}'", file=sys.stderr)
        sys.exit(1)

    print(f"Derived Key ({len(derived)} bytes): {derived.hex()}")


def cmd_checksum(args):
    """Generate or verify checksum manifest files."""
    if args.action == "create":
        _create_checksums(args)
    elif args.action == "verify":
        _verify_checksums(args)


def _create_checksums(args):
    from hashium.core import Hashium
    from hashium.experimental.hca import HCAHasher

    target_paths = []
    for path in args.targets:
        if os.path.isfile(path):
            target_paths.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in sorted(files):
                    target_paths.append(os.path.join(root, f))
        else:
            print(f"Warning: Target '{path}' does not exist", file=sys.stderr)

    lines = []
    h = Hashium()
    for fpath in target_paths:
        if args.algo == "hca":
            hasher = HCAHasher(output_bits=args.bits)
            with open(fpath, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            digest = hasher.hexdigest()
        else:
            digest = h.hash_file(fpath)
        rel_path = os.path.normpath(fpath).replace("\\", "/")
        lines.append(f"{digest}  {rel_path}\n")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"[OK] Checksum manifest written to '{args.out}' ({len(lines)} files)")
    else:
        for line in lines:
            sys.stdout.write(line)


def _verify_checksums(args):
    from hashium.core import Hashium
    from hashium.experimental.hca import HCAHasher

    if not os.path.exists(args.manifest):
        print(f"Error: Manifest file '{args.manifest}' not found", file=sys.stderr)
        sys.exit(1)

    h = Hashium()
    base_dir = os.path.dirname(os.path.abspath(args.manifest))
    passed = 0
    failed = 0

    with open(args.manifest, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            expected_hash, rel_path = parts[0].strip(), parts[1].strip()
            full_path = os.path.join(base_dir, rel_path)
            if not os.path.exists(full_path):
                # Try relative to current working directory
                full_path = os.path.abspath(rel_path)

            if not os.path.exists(full_path):
                print(f"[MISSING] {rel_path}")
                failed += 1
                continue

            # Determine algorithm from expected hash length or flag
            if len(expected_hash) == 64 and args.algo != "hca":
                computed = h.hash_file(full_path)
            else:
                bits = len(expected_hash) * 4
                hasher = HCAHasher(output_bits=bits)
                with open(full_path, "rb") as bf:
                    while chunk := bf.read(65536):
                        hasher.update(chunk)
                computed = hasher.hexdigest()

            if computed.lower() == expected_hash.lower():
                print(f"[OK] {rel_path}")
                passed += 1
            else:
                print(f"[FAILED] {rel_path} (expected {expected_hash[:8]}..., got {computed[:8]}...)")
                failed += 1

    print(f"\nVerification summary: {passed} passed, {failed} failed.")
    if failed > 0:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="hashium",
        description="Hashium CLI — Cryptography Toolkit & HCA-0.2 Engine",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: hash
    p_hash = subparsers.add_parser("hash", help="Compute cryptographic or HCA digests")
    p_hash.add_argument("-t", "--text", help="Text to hash")
    p_hash.add_argument("-f", "--file", help="File path to hash")
    p_hash.add_argument("-a", "--algo", choices=["hca", "sha256"], default="hca", help="Algorithm (default: hca)")
    p_hash.add_argument("-b", "--bits", type=int, default=256, help="Output bit length for HCA (128-4096, default: 256)")
    p_hash.add_argument("-s", "--salted", action="store_true", help="Generate a secure salted hash (<salt>:<hash>)")
    p_hash.set_defaults(func=cmd_hash)

    # Subcommand: encrypt
    p_enc = subparsers.add_parser("encrypt", help="Encrypt text or file using HCA-0.2 stream/AEAD cipher")
    p_enc.add_argument("-k", "--key", required=True, help="Secret encryption key")
    p_enc.add_argument("-t", "--text", help="Plaintext string")
    p_enc.add_argument("-f", "--file", help="Plaintext file path")
    p_enc.add_argument("-o", "--out", help="Output file path for ciphertext payload")
    p_enc.add_argument("--aead", action="store_true", help="Enable AEAD authenticated encryption mode with MAC tag")
    p_enc.add_argument("--ad", help="Associated metadata for AEAD mode (optional)")
    p_enc.set_defaults(func=cmd_encrypt)

    # Subcommand: decrypt
    p_dec = subparsers.add_parser("decrypt", help="Decrypt an HCA-0.2 encrypted payload")
    p_dec.add_argument("payload_pos", nargs="?", help="Encrypted payload string (e.g. <nonce>:<ciphertext>)")
    p_dec.add_argument("-k", "--key", help="Secret decryption key (will prompt if omitted)")
    p_dec.add_argument("-p", "--payload", help="Encrypted payload string (<nonce>:<ciphertext> or <nonce>:<tag>:<ciphertext>)")
    p_dec.add_argument("-f", "--file", help="Path to file containing encrypted payload")
    p_dec.add_argument("-o", "--out", help="Output file path for recovered plaintext")
    p_dec.add_argument("--ad", help="Associated metadata for AEAD mode (must match encryption)")
    p_dec.set_defaults(func=cmd_decrypt)

    # Subcommand: bench
    p_bench = subparsers.add_parser("bench", help="Run HCA benchmark suite")
    p_bench.set_defaults(func=cmd_benchmark)

    # Subcommand: shred
    p_shred = subparsers.add_parser("shred", help="Securely overwrite and shred files")
    p_shred.add_argument("files", nargs="+", help="File(s) to shred")
    p_shred.add_argument("-p", "--passes", type=int, default=3, help="Number of overwrite passes (default: 3)")
    p_shred.add_argument("-m", "--method", choices=["dod", "random", "zero"], default="dod", help="Overwrite pattern (default: dod)")
    p_shred.set_defaults(func=cmd_shred)

    # Subcommand: kdf
    p_kdf = subparsers.add_parser("kdf", help="Key derivation functions (HKDF, Scrypt)")
    p_kdf.add_argument("type", choices=["hkdf", "scrypt"], help="KDF primitive")
    p_kdf.add_argument("-p", "--password", required=True, help="Input keying material or password")
    p_kdf.add_argument("-s", "--salt", help="Salt string")
    p_kdf.add_argument("-l", "--length", type=int, default=32, help="Derived key length in bytes (default: 32)")
    p_kdf.add_argument("--info", help="Context information for HKDF")
    p_kdf.add_argument("--hash", default="sha256", help="Underlying hash for HKDF (default: sha256)")
    p_kdf.add_argument("--cost-n", type=int, default=16384, help="Scrypt CPU/memory cost parameter N")
    p_kdf.add_argument("--block-r", type=int, default=8, help="Scrypt block size parameter r")
    p_kdf.add_argument("--parallel-p", type=int, default=1, help="Scrypt parallelization parameter p")
    p_kdf.set_defaults(func=cmd_kdf)

    # Subcommand: checksum
    p_chk = subparsers.add_parser("checksum", help="Create and verify checksum manifest files")
    p_chk_sub = p_chk.add_subparsers(dest="action", required=True)

    p_chk_create = p_chk_sub.add_parser("create", help="Create a checksum manifest")
    p_chk_create.add_argument("targets", nargs="+", help="Files or directories to hash")
    p_chk_create.add_argument("-a", "--algo", choices=["sha256", "hca"], default="sha256", help="Hash algorithm")
    p_chk_create.add_argument("-b", "--bits", type=int, default=256, help="HCA output bit length (default: 256)")
    p_chk_create.add_argument("-o", "--out", help="Output file path for manifest")
    p_chk_create.set_defaults(func=cmd_checksum)

    p_chk_verify = p_chk_sub.add_parser("verify", help="Verify files against a manifest")
    p_chk_verify.add_argument("manifest", help="Path to checksum manifest file")
    p_chk_verify.add_argument("-a", "--algo", choices=["sha256", "hca"], default="sha256", help="Expected hash algorithm")
    p_chk_verify.set_defaults(func=cmd_checksum)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
