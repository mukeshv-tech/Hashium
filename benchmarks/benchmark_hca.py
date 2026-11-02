"""
Benchmarks for HCA-0.2 Native Prototype.
Compares HCA against standard SHA-256 and SHA3-256 (hashlib) and BLAKE3 (if available)
across 64 B, 1 KB, 1 MB, and 10 MB inputs.

DISCLAIMER: HCA-0.2 is an experimental hash construction and NOT a proven
cryptographic hash function. Benchmarks are provided for performance comparison only.
"""

import os
import sys
import time
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hashium.experimental.hca import hca

try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False


def run_benchmark():
    sizes = [
        ("64 B", 64, 10000),
        ("1 KB", 1024, 5000),
        ("1 MB", 1024 * 1024, 20),
        ("10 MB", 10 * 1024 * 1024, 3),
    ]

    print("=" * 80)
    print("HCA-0.2 BENCHMARK RESULTS")
    print("DISCLAIMER: HCA-0.2 is experimental. Throughput does NOT indicate security.")
    print("=" * 80)
    print(f"{'Input Size':<10} | {'Algorithm':<15} | {'Total Time (s)':<15} | {'Throughput (MB/s)':<18}")
    print("-" * 80)

    for name, size_bytes, iterations in sizes:
        # Generate predictable test data
        data = b"H" * size_bytes

        # Benchmark HCA-0.2 (256 bits)
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hca(data, output_bits=256)
        hca_time = time.perf_counter() - start
        hca_mb_s = (size_bytes * iterations) / (1024 * 1024) / hca_time
        print(f"{name:<10} | {'HCA-0.2 (256b)':<15} | {hca_time:<15.4f} | {hca_mb_s:<18.2f}")

        # Benchmark HCA-0.2 (512 bits)
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hca(data, output_bits=512)
        hca512_time = time.perf_counter() - start
        hca512_mb_s = (size_bytes * iterations) / (1024 * 1024) / hca512_time
        print(f"{name:<10} | {'HCA-0.2 (512b)':<15} | {hca512_time:<15.4f} | {hca512_mb_s:<18.2f}")

        # Benchmark SHA-256
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hashlib.sha256(data).digest()
        sha256_time = time.perf_counter() - start
        sha256_mb_s = (size_bytes * iterations) / (1024 * 1024) / sha256_time
        print(f"{name:<10} | {'SHA-256':<15} | {sha256_time:<15.4f} | {sha256_mb_s:<18.2f}")

        # Benchmark SHA3-256
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hashlib.sha3_256(data).digest()
        sha3_time = time.perf_counter() - start
        sha3_mb_s = (size_bytes * iterations) / (1024 * 1024) / sha3_time
        print(f"{name:<10} | {'SHA3-256':<15} | {sha3_time:<15.4f} | {sha3_mb_s:<18.2f}")

        if HAS_BLAKE3:
            start = time.perf_counter()
            for _ in range(iterations):
                _ = blake3.blake3(data).digest()
            blake3_time = time.perf_counter() - start
            blake3_mb_s = (size_bytes * iterations) / (1024 * 1024) / blake3_time
            print(f"{name:<10} | {'BLAKE3':<15} | {blake3_time:<15.4f} | {blake3_mb_s:<18.2f}")

        print("-" * 80)


if __name__ == "__main__":
    run_benchmark()
