"""
Cryptanalysis Experiment Script 3: Output Statistical Distribution & Monobit/Runs Tests
Part of HCA-0.4 Research Package.
Examines bit frequency, byte distribution, serial correlation, and prefix consistency.
"""

import os
import sys
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from hashium.experimental.hca import hca

def monobit_test(bitstring: str) -> float:
    """NIST SP 800-22 Frequency (Monobit) Test."""
    n = len(bitstring)
    s_n = sum(1 if b == '1' else -1 for b in bitstring)
    s_obs = abs(s_n) / math.sqrt(n)
    p_value = math.erfc(s_obs / math.sqrt(2))
    return p_value

def runs_test(bitstring: str) -> float:
    """NIST SP 800-22 Runs Test."""
    n = len(bitstring)
    ones = bitstring.count('1')
    pi = ones / n
    if abs(pi - 0.5) >= (2 / math.sqrt(n)):
        return 0.0 # Failed frequency requirement
    # Count runs
    v_obs = 1 + sum(1 for i in range(n - 1) if bitstring[i] != bitstring[i+1])
    num = abs(v_obs - 2 * n * pi * (1 - pi))
    den = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    p_value = math.erfc(num / den)
    return p_value

def run_experiment_3():
    print("=" * 70)
    print("EXPERIMENT 3: OUTPUT DISTRIBUTION, RUNS & BIT FREQUENCY")
    print("=" * 70)

    # 1. Generate 500 distinct 512-bit digests from sequential counters
    total_bits = 0
    total_ones = 0
    p_values_monobit = []
    p_values_runs = []

    print("[EXPERIMENTALLY OBSERVED] Testing 500 consecutive 512-bit digests (NIST SP 800-22 Monobit & Runs):")
    for i in range(500):
        data = f"Statistical_Test_Message_{i}".encode("utf-8")
        digest = hca(data, 512)
        bit_str = "".join(f"{b:08b}" for b in digest)
        total_bits += len(bit_str)
        total_ones += bit_str.count("1")

        p_m = monobit_test(bit_str)
        p_r = runs_test(bit_str)
        p_values_monobit.append(p_m)
        p_values_runs.append(p_r)

    overall_pi = total_ones / total_bits
    monobit_pass_rate = sum(1 for p in p_values_monobit if p >= 0.01) / len(p_values_monobit) * 100
    runs_pass_rate = sum(1 for p in p_values_runs if p >= 0.01) / len(p_values_runs) * 100

    print(f"  Total bits evaluated: {total_bits:,}")
    print(f"  Overall proportion of 1s: {overall_pi:.5f} (Ideal: 0.50000)")
    print(f"  Monobit Test Pass Rate (alpha=0.01): {monobit_pass_rate:.1f}%")
    print(f"  Runs Test Pass Rate (alpha=0.01):    {runs_pass_rate:.1f}%")

    # 2. Output prefix consistency check across variable output lengths
    print("\n[MATHEMATICALLY ESTABLISHED] Testing Output Prefix Consistency:")
    test_msg = b"Prefix consistency validation payload across variable lengths"
    dig128 = hca(test_msg, 128)
    dig256 = hca(test_msg, 256)
    dig512 = hca(test_msg, 512)
    dig1024 = hca(test_msg, 1024)

    assert dig128 == dig256[:16], "128-bit is not prefix of 256-bit"
    assert dig256 == dig512[:32], "256-bit is not prefix of 512-bit"
    assert dig512 == dig1024[:64], "512-bit is not prefix of 1024-bit"
    print("  [PASS] Output satisfies sponge prefix-consistency: HCA(M, L1) == HCA(M, L2)[0..L1/8] for L1 <= L2.")

if __name__ == "__main__":
    run_experiment_3()
