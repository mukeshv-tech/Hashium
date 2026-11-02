# HCA-0.4 Research: Diffusion & Differential Analysis

## 1. Experimental Methodology

Diffusion was tested empirically using `tests/research/exp2_diffusion_avalanche.py`.
The objective was to quantify the propagation of discrete bit differences across varying message lengths, byte positions, and multi-bit perturbations.

All tests measured Hamming distance $\Delta_H(H(M), H(M \oplus \Delta))$ for 512-bit output digests (ideal mean: 256.0 bits, 50.0%).

---

## 2. Experimental Results

### 2.1 Single-Bit Perturbations by Payload Size
Tested across 24 single-bit flips per payload size (first byte, middle byte, last byte across all 8 bit positions):

| Payload Size | Sample Size | Mean Flipped Bits | Percentage | Min Flipped | Max Flipped | Classification |
|---|---|---|---|---|---|---|
| **1 Byte** | 24 | 260.2 / 512 | **50.83%** | 239 | 275 | [EXPERIMENTALLY OBSERVED] |
| **32 Bytes** | 24 | 254.2 / 512 | **49.66%** | 232 | 278 | [EXPERIMENTALLY OBSERVED] |
| **63 Bytes** | 24 | 258.8 / 512 | **50.55%** | 231 | 278 | [EXPERIMENTALLY OBSERVED] |
| **64 Bytes** (Boundary) | 24 | 253.7 / 512 | **49.55%** | 234 | 281 | [EXPERIMENTALLY OBSERVED] |
| **128 Bytes** (2 Blocks) | 24 | 256.7 / 512 | **50.14%** | 234 | 275 | [EXPERIMENTALLY OBSERVED] |
| **500 Bytes** (8 Blocks) | 24 | 250.3 / 512 | **48.89%** | 227 | 282 | [EXPERIMENTALLY OBSERVED] |

### 2.2 Multi-Bit Perturbations (64-byte payload)
Measured across 50 random trials for each Hamming weight difference:

| Flipped Input Bits | Mean Output Flips | Percentage | Min Flipped | Max Flipped | Classification |
|---|---|---|---|---|---|
| **2 Bits** | 253.8 / 512 | **49.57%** | 230 | 283 | [EXPERIMENTALLY OBSERVED] |
| **4 Bits** | 256.5 / 512 | **50.09%** | 232 | 285 | [EXPERIMENTALLY OBSERVED] |
| **8 Bits** | 256.0 / 512 | **50.00%** | 232 | 281 | [EXPERIMENTALLY OBSERVED] |
| **16 Bits** | 255.2 / 512 | **49.85%** | 221 | 279 | [EXPERIMENTALLY OBSERVED] |
| **32 Bits** | 253.4 / 512 | **49.50%** | 234 | 271 | [EXPERIMENTALLY OBSERVED] |

---

## 3. Findings & Limitations

- **[EXPERIMENTALLY OBSERVED]**: Across all tested input sizes and bit offsets, flipping any single input bit produces an average of 48.9% to 50.8% output bit differences, consistent with the Strict Avalanche Criterion (SAC).
- **[MATHEMATICALLY ESTABLISHED]**: Bit diffusion across rounds is accelerated by the combination of word rotation coprime to 64 and inter-round permutation $\pi_r(i) = (5i + r) \bmod 16$.
- **[CRITICAL CAVEAT]**: Good avalanche behavior and passing SAC tests are **necessary** properties of a modern hash function, but they are **not sufficient** to prove security against dedicated differential or algebraic cryptanalysis. Many insecure or broken constructions (including MD4, MD5, and early SHA-1 prototypes) satisfy the Strict Avalanche Criterion.
