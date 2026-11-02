# HCA-0.2: Hashium Custom Algorithm Formal Specification

**Version:** 0.2 (Native Prototype)  
**Status:** Experimental / Non-Standardized  
**Author:** Hashium Development Team

> [!WARNING]
> **Experimental Primitive**: HCA-0.2 is an experimental hash construction created for research and educational purposes. It has not undergone peer review or rigorous cryptanalysis. It must NEVER be used for passwords, authentication, digital signatures, encryption, financial systems, or security-critical applications.

---

## 1. Parameters & Overview

| Property | Value | Description |
|---|---|---|
| Algorithm Name | Hashium Custom Algorithm | Experimental sponge-like hashing construction |
| Identifier | `HCA-0.2` | Protocol and header identifier |
| State Size | 1024 bits | 16 × 64-bit unsigned words |
| Word Size | 64 bits | Unsigned, big-endian representation |
| Block Size | 64 bytes (512 bits) | Input absorption block |
| Rate ($r$) | 512 bits | Rate capacity ratio: 512 / 512 |
| Capacity ($c$) | 512 bits | Sponge capacity words $S[8..15]$ |
| Permutation Rounds | 12 | Mixing rounds per block / squeeze |
| Output Range | 128 to 4096 bits | Variable length in increments of 8 bits (1 byte) |

---

## 2. SplitMix64 Deterministic Constant Generator

A deterministic pseudo-random stream is derived from SplitMix64 using seed:
$$\text{SEED} = \text{0x4843412D76303100} \quad (\text{"HCA-v01\0"})$$

### Generator Recurrence
Let $x_0 = \text{SEED}$. For each generated 64-bit integer $G[k]$ ($k = 0, 1, 2, \dots$):

$$x_{k+1} = (x_k + \text{0x9E3779B97F4A7C15}) \bmod 2^{64}$$
$$z = x_{k+1}$$
$$z = (z \oplus (z \gg 30)) \times \text{0xBF58476D1CE4E5B9} \bmod 2^{64}$$
$$z = (z \oplus (z \gg 27)) \times \text{0x94D049BB133111EB} \bmod 2^{64}$$
$$G[k] = z \oplus (z \gg 31)$$

All arithmetic is unsigned 64-bit wrapping operations.

---

## 3. Initial State Constants ($IV$)

The state $S = (S[0], S[1], \dots, S[15])$ comprises 16 unsigned 64-bit words (1024 bits total).

The initial state constants are the first 16 values produced by the SplitMix64 generator:
$$IV[i] = G[i] \quad \text{for } i \in [0, 15]$$

---

## 4. Round Constants ($RC$)

The mixing transformation uses 12 rounds, with 16 constants per round (total 192 constants).
These are taken sequentially as the next 192 values produced by SplitMix64:
$$RC[r][i] = G[16 + 16 \times r + i] \quad \text{for } r \in [0, 11], \, i \in [0, 15]$$

---

## 5. Twelve-Round Experimental Mixing Transformation

A single execution of the 12-round mixing transformation maps state $S$ to $S'$.

For round $r = 0, 1, \dots, 11$, from the round input state $S$:
1. **First Stage ($A$):**
   $$A[i] = S[i] + \text{ROTL64}(S[(i+1) \bmod 16] \oplus RC[r][i], \, 13) \pmod{2^{64}}$$

2. **Second Stage ($B$):**
   $$B[i] = \text{ROTL64}(S[(i+4) \bmod 16] + S[(i+11) \bmod 16], \, (7i + 3r) \bmod 64)$$

3. **Combined Stage ($T$):**
   $$T[i] = \text{ROTL64}(A[i] \oplus B[i], \, (11i + 7r + 1) \bmod 64)$$

4. **Diffusion / Permutation ($S_{\text{new}}$):**
   $$S_{\text{new}}[i] = T[(5i + r) \bmod 16]$$

> [!IMPORTANT]
> - All intermediate values $A[i], B[i], T[i]$ are evaluated from the original round input state $S$. No in-place state replacement is performed until all 16 words of $S_{\text{new}}$ are computed.
> - Exactly 12 rounds are applied in sequence.

---

## 6. Padding

Given a byte string $M$ of length $L = \text{len}(M)$ bytes ($8L$ bits):
1. Fail if $8L \ge 2^{64}$ (cannot be represented as a 64-bit unsigned integer).
2. Append single byte `0x01`.
3. Append $k$ zero bytes (`0x00`), where $k \ge 0$ is the smallest integer such that:
   $$(L + 1 + k) \equiv 56 \pmod{64}$$
4. Append the 8-byte big-endian representation of $8L$:
   $$\text{BE64}(8 \times L)$$

The padded message $M'$ has a length that is a strict positive multiple of 64 bytes.

---

## 7. Message Absorption

Initialize state:
$$S[i] = IV[i] \quad \text{for } i \in [0, 15]$$

Divide $M'$ into $N$ blocks of 64 bytes: $B_0, B_1, \dots, B_{N-1}$.

For each block $j \in [0, N-1]$:
1. Decode $B_j$ as eight 64-bit big-endian words $M_j[0..7]$:
   $$M_j[i] = \text{BE64\_TO\_U64}(B_j[8i .. 8i+7]) \quad \text{for } i \in [0, 7]$$
2. Absorb message words:
   $$S[i] = S[i] \oplus M_j[i] \quad \text{for } i \in [0, 7]$$
3. Absorb block index into capacity:
   $$S[8] = S[8] \oplus j$$
4. Absorb domain separator:
   $$S[9] = S[9] \oplus \text{0x4843414142534F52} \quad (\text{"HCAABSOR"})$$
5. Apply the 12-round mixing transformation to $S$.

---

## 8. Squeezing / Output Generation

Let $D$ be the requested digest size in bits, where $128 \le D \le 4096$ and $D \equiv 0 \pmod 8$.  
Let $B_{\text{req}} = D / 8$ bytes.

Output buffer starts empty.  
For squeeze iteration $q = 0, 1, 2, \dots$:
1. Apply domain separator and squeeze counter:
   $$S[14] = S[14] \oplus \text{0x4843414F55545055} \quad (\text{"HCAOUTPU"})$$
   $$S[15] = S[15] \oplus q$$
2. Apply the 12-round mixing transformation to $S$.
3. Squeeze rate words $S[0..7]$ into 64 bytes (big-endian encoding):
   $$\text{block\_bytes} = \text{BE64}(S[0]) \parallel \text{BE64}(S[1]) \parallel \dots \parallel \text{BE64}(S[7])$$
4. Append $\text{block\_bytes}$ to output buffer.
5. If output buffer length $\ge B_{\text{req}}$, truncate to $B_{\text{req}}$ bytes and terminate.
