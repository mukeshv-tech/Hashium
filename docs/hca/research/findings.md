# HCA-0.4 Research: Consolidated Findings & Design Review

## 1. Summary of Completed Research

During the HCA-0.4 phase, the Hashium Custom Algorithm (HCA-0.1 through HCA-0.3) was subjected to systematic independent cryptanalysis, structural modeling, and empirical verification.

No modifications to constants, rounds, padding, or algorithm logic were made during this phase.

---

## 2. Categorized Findings

### 2.1 [MATHEMATICALLY ESTABLISHED]
1. **Bijective Word Permutation:** The inter-round mapping $\pi_r(i) = (5i + r) \bmod 16$ is a complete bijection for all rounds $r \in [0, 11]$. No state entropy is lost in permutation.
2. **Rapid Word Dependency:** Every state word depends algebraically on all sixteen input words by **Round 3** (25% into the 12-round cycle).
3. **Prefix Consistency:** Squeezed digests satisfy prefix equivalence: $\text{HCA}(M, L_1) = \text{HCA}(M, L_2)[0 \dots L_1/8]$ for $L_1 \le L_2$.
4. **Length Extension Resistance:** The 512-bit capacity barrier ($c = 512$) guarantees that unobserved internal state bits prevent classical Merkle-Damgård length-extension attacks.
5. **Padding Unambiguity:** Bit-length suffixed padding guarantees that messages of different lengths or contents never map to identical block sequences.
6. **Block Counter Overflow Floor:** The 64-bit block counter in $s_8$ requires $1\text{ Zettabyte}$ of continuous data before wrapping.

### 2.2 [EXPERIMENTALLY OBSERVED]
1. **Avalanche Saturation:** Single-bit input changes cause an average of **48.9% to 50.8%** of digest bits to flip, matching Strict Avalanche Criterion (SAC) targets.
2. **Statistical Uniformity:** Consecutive outputs pass NIST SP 800-22 Monobit (99.4%) and Runs (98.8%) tests with a mean bit proportion of $\pi = 0.50027$.
3. **Absence of Trivial Fixed Points:** Both the all-zero state ($0^{1024}$) and all-ones state ($1^{1024}$) are disrupted by SplitMix64 round constants and produce pseudorandom outputs.
4. **Birthday Paradox Compliance:** In a 24-bit truncated toy model, collisions appeared at 2,090 evaluations, conforming to normal birthday probability.

### 2.3 [HYPOTHESIS]
1. **Distinguisher Penetration Depth:** Because modular addition carries propagate non-linearly across cyclic rotations, linear/differential distinguishers are hypothesized to penetrate no further than 5 to 6 rounds.
2. **Algebraic Complexity Growth:** The algebraic degree of the state bits is hypothesized to reach full polynomial saturation ($d = 1023$) by Round 6.

### 2.4 [UNKNOWN]
1. **Higher-Order Differential Bounds:** Formal upper bounds on higher-order differential characteristics across the full 12 rounds have not been mathematically proven.
2. **SAT-Solver Preimage Complexity:** The exact computational complexity of inverting a 4-round or 6-round toy model using modern SAT/SMT solvers remains unmeasured.

---

## 3. Structural Weaknesses & Specification Ambiguities

1. **Weakness 1: Single-Word Domain Injection ($s_9$):**
   Injecting domain separation exclusively into word $s_9$ concentrates domain isolation into one 64-bit register. Spreading domain separation across multiple capacity words (e.g., $s_9, s_{10}$) would enhance structural defense.
2. **Weakness 2: String-Prefixed Tree Hashing vs. State Domain Tags:**
   Parallel tree hashing injects ASCII headers (`"HCALEAF:"`, `"HCATREE:"`) into the message stream rather than utilizing dedicated capacity domain words in $s_9$. While collision-free, this is suboptimal compared to native state domain separation.
3. **Ambiguity 1: Sub-Byte Bitlengths:**
   The specification mandates that inputs be byte-aligned and output bitlengths be multiples of 8. Fractional-bit inputs (e.g., 7 bits) are undefined.

---

## 4. Recommendations for HCA-0.5

1. **Do NOT promote HCA to production:**
   HCA must strictly remain under `hashium.experimental.hca`. It should not be recommended for passwords, digital signatures, or security-critical systems.
2. **Automated SAT/SMT Cryptanalysis Harness:**
   Implement an automated SAT solver script (using Z3 or CryptoMiniSat) to systematically search for differential trails and preimages on reduced-round variants (1 to 6 rounds).
3. **Formalized Capacity Injection:**
   In future revisions (HCA-0.5), consider formalizing state-level domain constants in capacity registers for tree hashing rather than message-level string prefixes.
