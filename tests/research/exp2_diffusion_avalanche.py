"""
Cryptanalysis Experiment Script 2: Differential Diffusion & Avalanche Analysis
Part of HCA-0.4 Research Package.
Tests how 1-bit and multi-bit differences propagate across message positions, lengths,
and examines Strict Avalanche Criterion (SAC) bit independence.
"""

import os
import sys
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from hashium.experimental.hca import hca

def count_differing_bits(b1: bytes, b2: bytes) -> int:
    diff = 0
    for x, y in zip(b1, b2):
        diff += bin(x ^ y).count("1")
    return diff

def run_experiment_2():
    print("=" * 70)
    print("EXPERIMENT 2: DIFFERENTIAL DIFFUSION & AVALANCHE ANALYSIS")
    print("=" * 70)

    # 1. Single-bit input changes across different positions within an input block
    print("\n[EXPERIMENTALLY OBSERVED] 1. Single-Bit Input Perturbation (512-bit digest):")
    sample_sizes = [0, 1, 32, 63, 64, 128, 500]
    trials_per_size = 50

    for size in sample_sizes:
        base_msg = b"A" * size if size > 0 else b""
        total_bit_flips = 0
        total_evals = 0
        min_flips = 512
        max_flips = 0

        h_base = hca(base_msg, 512)
        target_indices = [0] if size == 0 else [0, size // 2, size - 1]

        for byte_idx in target_indices:
            if size == 0:
                break
            for bit_pos in range(8):
                mutated = bytearray(base_msg)
                mutated[byte_idx] ^= (1 << bit_pos)
                h_mut = hca(bytes(mutated), 512)
                flips = count_differing_bits(h_base, h_mut)
                total_bit_flips += flips
                total_evals += 1
                if flips < min_flips: min_flips = flips
                if flips > max_flips: max_flips = flips

        if total_evals > 0:
            avg_flips = total_bit_flips / total_evals
            pct = (avg_flips / 512.0) * 100
            print(f"  Payload {size:3d} bytes | Tested: {total_evals:2d} | Avg Flips: {avg_flips:5.1f} / 512 ({pct:5.2f}%) | Min: {min_flips} | Max: {max_flips}")

    # 2. Multi-bit input changes (2, 3, 4, 8 bits flipped)
    print("\n[EXPERIMENTALLY OBSERVED] 2. Multi-Bit Input Differences (64-byte payload):")
    base_msg = b"\x55" * 64
    h_base = hca(base_msg, 512)
    for flip_count in [2, 4, 8, 16, 32]:
        flips_record = []
        for _ in range(50):
            mutated = bytearray(base_msg)
            # Pick distinct bit positions
            chosen_bits = random.sample(range(64 * 8), flip_count)
            for b in chosen_bits:
                byte_i = b // 8
                bit_i = b % 8
                mutated[byte_i] ^= (1 << bit_i)
            h_mut = hca(bytes(mutated), 512)
            flips_record.append(count_differing_bits(h_base, h_mut))
        avg_f = sum(flips_record) / len(flips_record)
        print(f"  Flipped {flip_count:2d} input bits | Avg Output Flips: {avg_f:5.1f} / 512 ({(avg_f/512)*100:5.2f}%) | Min: {min(flips_record)} | Max: {max(flips_record)}")

    # 3. Output lengths 128, 256, 512, 1024, 2048, 4096 bits
    print("\n[EXPERIMENTALLY OBSERVED] 3. Avalanche across Variable Output Lengths:")
    for out_bits in [128, 256, 512, 1024, 2048]:
        h1 = hca(b"Avalanche Test A", out_bits)
        h2 = hca(b"Avalanche Test B", out_bits)
        flips = count_differing_bits(h1, h2)
        print(f"  Output {out_bits:4d} bits | Flipped: {flips:4d} / {out_bits} ({(flips/out_bits)*100:5.2f}%)")

if __name__ == "__main__":
    run_experiment_2()
