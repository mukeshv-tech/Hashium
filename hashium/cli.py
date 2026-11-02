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
        with open(args.file, "rb") as f:
            data = f.read()
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
        digest = hca(data, output_bits=args.bits)
        print(digest.hex())
    elif args.algo == "sha256":
        h = Hashium()
        if args.file:
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
        print("Error: Provide payload string as argument/flag (-p/--payload), input file (-f), or pipe via terminal.", file=sys.stderr)
        sys.exit(1)

    try:
        parts = payload.split(":")
        if len(parts) == 3:  # AEAD format: nonce:tag:ciphertext
            ad = args.ad or ""
            plaintext = hca_aead_decrypt(payload, args.key, associated_data=ad)
        elif len(parts) == 2:  # Stream format: nonce:ciphertext
            plaintext = hca_decrypt(payload, args.key)
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
    p_dec.add_argument("payload_pos", nargs="?", help="Encrypted payload positional string (optional)")
    p_dec.add_argument("-k", "--key", required=True, help="Secret decryption key")
    p_dec.add_argument("-p", "--payload", help="Encrypted payload string (<nonce>:<ciphertext> or <nonce>:<tag>:<ciphertext>)")
    p_dec.add_argument("-f", "--file", help="Path to file containing encrypted payload")
    p_dec.add_argument("-o", "--out", help="Output file path for recovered plaintext")
    p_dec.add_argument("--ad", help="Associated metadata for AEAD mode (must match encryption)")
    p_dec.set_defaults(func=cmd_decrypt)

    # Subcommand: bench
    p_bench = subparsers.add_parser("bench", help="Run HCA benchmark suite")
    p_bench.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
