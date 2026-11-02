# HCA-0.3 Security & Cryptanalysis Analysis

**Status:** Experimental Research Primitive  
**Author:** Hashium Security Team  

> [!WARNING]
> **Experimental Primitive**: HCA-0.3 is an experimental hash construction created for research and educational purposes. It has not undergone formal academic peer review or dedicated cryptanalysis. It must NEVER be used for passwords, authentication, digital signatures, encryption, financial systems, or security-critical applications.

---

## 1. Mixing Function Properties & Algebraic Structure

HCA-0.3 relies on an Addition-Rotation-XOR (ARX-like) 12-round mixing transformation over a 1024-bit state represented as sixteen 64-bit unsigned words $S[0..15]$:

1. **First Stage ($A$):**
   $$A[i] = S[i] + \text{ROTL64}(S[(i+1) \bmod 16] \oplus RC[r][i], \, 13) \pmod{2^{64}}$$
2. **Second Stage ($B$):**
   $$B[i] = \text{ROTL64}(S[(i+4) \bmod 16] + S[(i+11) \bmod 16], \, (7i + 3r) \bmod 64)$$
3. **Combination ($T$):**
   $$T[i] = \text{ROTL64}(A[i] \oplus B[i], \, (11i + 7r + 1) \bmod 64)$$
4. **Diffusion Stride:**
   $$S_{\text{new}}[i] = T[(5i + r) \bmod 16]$$

### Observations:
- **Absence of S-Boxes**: Non-linearity is derived solely from the carry chains of 64-bit modular addition and the bitwise XOR operation.
- **Dynamic Rotations**: Rotations vary across rounds and word indices ($7i + 3r$ and $11i + 7r + 1$), disrupting fixed-stride bit alignment across rounds.

---

## 2. Invertibility & Permutation Bijectivity Weaknesses

- **Unproven Bijectivity**: The transformation $S \to S_{\text{new}}$ has not been formally proven to be a bijection over $\{0, 1\}^{1024}$.
- **Entropy Collapse Risk**: In an unproven mixing function, collisions inside intermediate rounds could reduce the effective state space over many rounds or long message absorptions. Standard sponge constructions (such as Keccak in SHA-3 or Ascon) require the round function to be a strict mathematical permutation (invertible bijection). Until bijectivity is proven, HCA must be regarded as an *iterated mixing function*, not a true cryptographic permutation.

---

## 3. Strict Avalanche Criterion (SAC) & Bit Diffusion

- **Avalanche Behavior**: In empirical testing, a single input bit flip achieves approximately 50% bit divergence across the 512-bit output within 3 to 4 rounds.
- **Statistical Significance**: Passing statistical randomness batteries (such as uniform byte distribution or bit independence) is a necessary condition, but is **NOT** sufficient evidence of cryptographic security or collision resistance.

---

## 4. Collision Resistance & Squeezing Vulnerabilities

- **Capacity ($c = 512$ bits)**: In an ideal sponge, generic collision resistance is bounded by $2^{c/2} = 2^{256}$.
- **Rate ($r = 512$ bits)**: The 512-bit rate allows rapid absorption, but because half the state is overwritten/XORed each block, structural weaknesses in the mixing function could permit differential fault injection or state manipulation in fewer than $2^{256}$ operations.

---

## 5. Length-Extension Considerations

- Standard Merkle-Damgård hashes without truncation (such as raw SHA-256) are vulnerable to length-extension attacks.
- HCA-0.3 mitigates classic length-extension through:
  1. **Capacity Words ($S[8..15]$)**: Only words $S[0..7]$ are exposed in squeezed outputs. The 512-bit internal capacity is never directly emitted.
  2. **Domain Separation**:
     - Absorption injects block counter $S[8] \oplus j$ and domain tag $S[9] \oplus \text{"HCAABSOR"}$.
     - Output extraction injects squeeze counter $S[15] \oplus q$ and domain tag $S[14] \oplus \text{"HCAOUTPU"}$.
- This strict domain separation prevents an attacker from continuing a hash chain from an observed output digest.

---

## 6. Distinguishers & Known Limitations

1. **Zero-Block Invariants**: If the state encounters a weak invariant under specific round constants, rotational distinguishers could be constructed.
2. **Side-Channel Vulnerability**: The reference implementation and general scalar wrapping operations do not have formal hardware constant-time verification against cache timing or power analysis attacks.
3. **Experimental Recommendation**: HCA-0.3 must remain confined to `hashium.experimental.hca` for academic exploration and non-critical checksumming.
