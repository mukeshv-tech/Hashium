# HCA-0.4 Research: Collision and Distinguishability Review

## 1. Collision Resistance Analysis

### 1.1 Classical Birthday Bound
In any hash function with digest length $L$ bits, generic collision search requires approximately $2^{L/2}$ evaluations by the Birthday Paradox.
- For HCA-256: Birthday bound is $2^{128}$ evaluations.
- For HCA-512: Birthday bound is $2^{256}$ evaluations.

### 1.2 Sponge Capacity Collision Bound
- **[MATHEMATICALLY ESTABLISHED]**: In a cryptographic sponge construction with capacity $c = 512$ bits, internal state collisions require at least $2^{c/2} = 2^{256}$ calls to the permutation $\mathcal{M}$ (assuming an ideal permutation).
- **[EXPERIMENTALLY OBSERVED]**: In a truncated 24-bit toy model (`exp4_collision_domain.py`), birthday collisions appeared after 2,090 evaluations (theoretical expectation: $\approx \sqrt{\frac{\pi \cdot 2^{24}}{2}} \approx 5,134$ evaluations). The distribution conforms to classical birthday statistics.
- **[CRITICAL CAVEAT]**: The inability to find full 512-bit collisions via brute force is an elementary consequence of the 512-bit search space and does **not** prove cryptographic collision resistance.

---

## 2. Multi-Collision Vulnerability Review

In iterated Merkle-Damgård constructions, Joux (2004) proved that finding $2^k$ multi-collisions requires only $k \cdot 2^{n/2}$ work instead of the random oracle bound $2^{n(k-1)/k}$.

- **[MATHEMATICALLY ESTABLISHED]**: Because HCA employs a wide 1024-bit state with 512 bits of capacity that are never revealed in standard 256-bit or 512-bit digests, Joux's classic multi-collision attack does not directly transfer to HCA. The capacity acts as an unobserved entropy buffer.
- **[HYPOTHESIS]**: Multi-collision attacks against HCA require finding internal state collisions in the full 1024-bit space or the 512-bit capacity, both of which require $\ge 2^{256}$ work under random permutation assumptions.

---

## 3. Potential Distinguishers

- **[HYPOTHESIS]**: Possible distinguishing attacks against reduced-round HCA:
  1. **Differential-Linear Distinguishers:** Linear approximations of modular addition combined with differential rotational trails may produce a distinguishing bias up to 4 or 5 rounds.
  2. **Integral / Higher-Order Differentials:** Because HCA uses only ARX operations (algebraic degree grows linearly per round), an integral distinguisher may exist for 3 to 4 rounds.
  3. **Rotational Distinguishers:** While SplitMix64 round constants inject asymmetric bits, reduced-round variants without constants would exhibit strong rotational invariants.

- **[UNKNOWN]**: Whether any distinguisher can penetrate past Round 6 in the presence of SplitMix64 constant injection and affine word permutation.
