"""
HCA-0.3 Comprehensive Benchmark Suite.
Measures Throughput (MB/s), Latency (us), and Peak Memory across sizes:
64 B, 1 KB, 1 MB, 10 MB.
Records system hardware, Python runtime, and CPU metadata.
"""

import os
import sys
import time
import platform
import psutil
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hashium.experimental.hca import hca

try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False


def get_system_info():
    return {
        "os": platform.platform(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "cpu_count": psutil.cpu_count(logical=True),
        "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
    }


def measure_memory_and_latency(func, data, iterations):
    process = psutil.Process()
    mem_before = process.memory_info().rss

    start = time.perf_counter()
    for _ in range(iterations):
        _ = func(data)
    elapsed = time.perf_counter() - start

    mem_after = process.memory_info().rss
    avg_latency_us = (elapsed / iterations) * 1_000_000
    throughput_mb_s = (len(data) * iterations) / (1024 * 1024) / elapsed
    delta_mem_kb = max(0, (mem_after - mem_before) / 1024)

    return throughput_mb_s, avg_latency_us, delta_mem_kb


def run_benchmark():
    info = get_system_info()
    print("=" * 95)
    print("                      HCA-0.3 BENCHMARK & SYSTEM ANALYSIS")
    print("=" * 95)
    print(f"OS: {info['os']} | CPU: {info['processor']} | Logical Cores: {info['cpu_count']}")
    print(f"Python: {info['python']} | Total RAM: {info['total_ram_gb']} GB")
    print("DISCLAIMER: HCA-0.3 is experimental. Throughput does NOT indicate cryptographic security.")
    print("=" * 95)
    print(f"{'Input Size':<10} | {'Algorithm':<15} | {'Throughput (MB/s)':<18} | {'Latency (us)':<14} | {'Memory (KB)':<12}")
    print("-" * 95)

    sizes = [
        ("64 B", 64, 10000),
        ("1 KB", 1024, 5000),
        ("1 MB", 1024 * 1024, 20),
        ("10 MB", 10 * 1024 * 1024, 5),
    ]

    for name, size, iters in sizes:
        buf = b"\x3C" * size

        # HCA-0.3 (256-bit)
        mb_s, lat, mem = measure_memory_and_latency(lambda d: hca(d, output_bits=256), buf, iters)
        print(f"{name:<10} | {'HCA-0.3 (256b)':<15} | {mb_s:<18.2f} | {lat:<14.2f} | {mem:<12.1f}")

        # HCA-0.3 (512-bit)
        mb_s, lat, mem = measure_memory_and_latency(lambda d: hca(d, output_bits=512), buf, iters)
        print(f"{name:<10} | {'HCA-0.3 (512b)':<15} | {mb_s:<18.2f} | {lat:<14.2f} | {mem:<12.1f}")

        # SHA-256
        mb_s, lat, mem = measure_memory_and_latency(lambda d: hashlib.sha256(d).digest(), buf, iters)
        print(f"{name:<10} | {'SHA-256':<15} | {mb_s:<18.2f} | {lat:<14.2f} | {mem:<12.1f}")

        # SHA3-256
        mb_s, lat, mem = measure_memory_and_latency(lambda d: hashlib.sha3_256(d).digest(), buf, iters)
        print(f"{name:<10} | {'SHA3-256':<15} | {mb_s:<18.2f} | {lat:<14.2f} | {mem:<12.1f}")

        if HAS_BLAKE3:
            mb_s, lat, mem = measure_memory_and_latency(lambda d: blake3.blake3(d).digest(), buf, iters)
            print(f"{name:<10} | {'BLAKE3':<15} | {mb_s:<18.2f} | {lat:<14.2f} | {mem:<12.1f}")

        print("-" * 95)


if __name__ == "__main__":
    run_benchmark()
