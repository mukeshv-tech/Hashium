"""
High-Scale Benchmarks for HCA-0.2 Native Prototype.
Tests large payloads up to 100 MB.

DISCLAIMER: HCA-0.2 is experimental. Throughput does NOT indicate security.
"""

import os
import sys
import time
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hashium.experimental.hca import hca, hca_parallel


def run_benchmark():
    sizes = [
        ("1 MB", 1 * 1024 * 1024, 20),
        ("10 MB", 10 * 1024 * 1024, 5),
        ("50 MB", 50 * 1024 * 1024, 2),
        ("100 MB", 100 * 1024 * 1024, 1),
    ]

    print("=" * 85)
    print("             HCA-0.2 HIGH-SCALE BENCHMARK RESULTS (UP TO 100 MB)")
    print("DISCLAIMER: HCA-0.2 is experimental. Throughput does NOT indicate security.")
    print("=" * 85)
    print(f"{'Input Size':<12} | {'Algorithm':<15} | {'Total Time (s)':<15} | {'Throughput (MB/s)':<18}")
    print("-" * 85)

    for name, size_bytes, iterations in sizes:
        # Pre-allocate contiguous test buffer
        data = b"\x5A" * size_bytes

        # HCA-0.2 (256 bits)
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hca(data, output_bits=256)
        hca_time = time.perf_counter() - start
        hca_mb_s = (size_bytes * iterations) / (1024 * 1024) / hca_time
        print(f"{name:<12} | {'HCA-0.2 (256b)':<15} | {hca_time:<15.4f} | {hca_mb_s:<18.2f}")

        # HCA-0.2 (512 bits)
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hca(data, output_bits=512)
        hca512_time = time.perf_counter() - start
        hca512_mb_s = (size_bytes * iterations) / (1024 * 1024) / hca512_time
        print(f"{name:<12} | {'HCA-0.2 (512b)':<15} | {hca512_time:<15.4f} | {hca512_mb_s:<18.2f}")

        # HCA-Parallel (Tree Hash 512b)
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hca_parallel(data, output_bits=512)
        hcapar_time = time.perf_counter() - start
        hcapar_mb_s = (size_bytes * iterations) / (1024 * 1024) / hcapar_time
        print(f"{name:<12} | {'HCA-Parallel':<15} | {hcapar_time:<15.4f} | {hcapar_mb_s:<18.2f}")

        # SHA-256
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hashlib.sha256(data).digest()
        sha256_time = time.perf_counter() - start
        sha256_mb_s = (size_bytes * iterations) / (1024 * 1024) / sha256_time
        print(f"{name:<12} | {'SHA-256':<15} | {sha256_time:<15.4f} | {sha256_mb_s:<18.2f}")

        # SHA3-256
        start = time.perf_counter()
        for _ in range(iterations):
            _ = hashlib.sha3_256(data).digest()
        sha3_time = time.perf_counter() - start
        sha3_mb_s = (size_bytes * iterations) / (1024 * 1024) / sha3_time
        print(f"{name:<12} | {'SHA3-256':<15} | {sha3_time:<15.4f} | {sha3_mb_s:<18.2f}")

        print("-" * 85)


if __name__ == "__main__":
    run_benchmark()
