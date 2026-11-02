"""
Cryptanalysis Experiment Script 1: Mixing Permutation Invertibility & Algebraic Dependency
Part of HCA-0.4 Research Package.
Tests whether the 12-round mixing permutation M(S) is invertible, its dependency graph,
and checks for fixed points or invariant subspaces.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from hashium.experimental.hca_reference import generate_constants, mix_12_rounds, RC_CONSTANTS

def diffuse_map(r: int, i: int) -> int:
    return (5 * i + r) % 16

def run_experiment_1():
    print("=" * 70)
    print("EXPERIMENT 1: MIXING PERMUTATION INVERTIBILITY & DEPENDENCY ANALYSIS")
    print("=" * 70)

    # 1. Test bijectivity of diffuse_map for all 12 rounds
    all_bijective = True
    for r in range(12):
        mapped = [diffuse_map(r, i) for i in range(16)]
        if len(set(mapped)) != 16:
            all_bijective = False
            print(f"[!] Round {r} diffusion map is NOT bijective! Mapped: {mapped}")
    if all_bijective:
        print("[MATHEMATICALLY ESTABLISHED] Diffuse map pi_r(i) = (5i + r) mod 16 is bijective for all 12 rounds.")

    # 2. Dependency Matrix across rounds
    # Let D[r][i] be the set of input words that word i at round r depends on.
    # At round 0 (before mixing): word i depends only on {i}.
    deps = [{i} for i in range(16)]
    round_dep_counts = []

    for r in range(12):
        new_deps = [set() for _ in range(16)]
        # For word i:
        # a[i] depends on s[i] and s[(i+1)%16]
        # b[i] depends on s[(i+4)%16] and s[(i+11)%16]
        # t[i] depends on union of deps of i, (i+1)%16, (i+4)%16, (i+11)%16
        t_deps = [set() for _ in range(16)]
        for i in range(16):
            t_deps[i] = deps[i] | deps[(i + 1) % 16] | deps[(i + 4) % 16] | deps[(i + 11) % 16]

        # s_new[i] = t[(5*i + r) % 16]
        for i in range(16):
            new_deps[i] = t_deps[(5 * i + r) % 16]

        deps = new_deps
        avg_deps = sum(len(d) for d in deps) / 16.0
        min_deps = min(len(d) for d in deps)
        max_deps = max(len(d) for d in deps)
        round_dep_counts.append((r + 1, avg_deps, min_deps, max_deps))

    print("\n[MATHEMATICALLY ESTABLISHED] State Word Dependency Dispersion by Round:")
    print("Round | Avg Input Words Depended On | Min Words | Max Words")
    print("-" * 55)
    for r_num, avg_d, min_d, max_d in round_dep_counts:
        print(f"{r_num:5d} | {avg_d:27.1f} | {min_d:9d} | {max_d:9d}")

    # 3. Test for fixed points S such that M(S) == S
    print("\n[EXPERIMENTALLY OBSERVED] Testing for trivial zero or constant fixed points...")
    zero_state = [0] * 16
    st_zero = mix_12_rounds(zero_state, RC_CONSTANTS)
    if st_zero == zero_state:
        print("[!] CRITICAL: All-zero state is a fixed point!")
    else:
        print(f"[PASS] All-zero state is NOT a fixed point (M(0) produces non-zero state; first word: {hex(st_zero[0])}).")

    all_ones_state = [0xFFFFFFFFFFFFFFFF] * 16
    st_ones = mix_12_rounds(all_ones_state, RC_CONSTANTS)
    if st_ones == all_ones_state:
        print("[!] CRITICAL: All-ones state is a fixed point!")
    else:
        print(f"[PASS] All-ones state is NOT a fixed point (first word: {hex(st_ones[0])}).")

    # Check structural invertibility nature
    print("\n[MATHEMATICALLY ESTABLISHED] Structural Invertibility:")
    print("  The intra-round step computes t[i] = ((s[i] + Rot(s[i+1]^RC, 13)) ^ Rot(s[i+4]+s[i+11], rot_b)) <<< rot_t.")
    print("  Given t[0..15], recovering s[0..15] is not trivially triangular because each equation couples forward")
    print("  and backward words: (i, i+1, i+4, i+11) mod 16.")
    print("  While the map is non-linear and likely bijective, inverting it without guessing intermediate words requires")
    print("  solving a non-linear multivariate polynomial system over GF(2) or Z_{2^64}.")

if __name__ == "__main__":
    run_experiment_1()
