# HCA-0.1 Design Notes

## 1. Architectural Philosophy
HCA-0.1 follows an iterated sponge-like paradigm operating on a 1024-bit state represented as 16 words of 64 bits each:
- **Rate ($r = 512$ bits)**: Words $S[0..7]$ are used for absorbing input message blocks and emitting squeezed output.
- **Capacity ($c = 512$ bits)**: Words $S[8..15]$ serve as internal state, preventing direct inversion and hosting domain separation tags.

## 2. SplitMix64 Constant Generation
The pseudorandom constant generation uses Sebastiano Vigna's SplitMix64 PRNG seeded with ASCII string `b"HCA-v01\0"` (`0x4843412D76303100`).
SplitMix64 guarantees:
- Full 64-bit period ($2^{64}$).
- Uniform distribution and passing BigCrush test battery.
- Nothing-up-my-sleeve deterministic constants without arbitrary magic numbers.

## 3. Round Function Mechanics
Each round computes temporary states $A, B, T$ and a final diffuse permutation:
1. **$A[i]$**: Adds rotated XOR of neighbor word $S[i+1]$ mixed with round constant $RC[r][i]$. Uses a fixed prime shift (13).
2. **$B[i]$**: Sums words from different quarters ($i+4$ and $i+11$) and rotates by round/index-dependent dynamic offset $(7i + 3r) \bmod 64$.
3. **$T[i]$**: Non-linearly mixes $A[i]$ and $B[i]$ with rotation $(11i + 7r + 1) \bmod 64$.
4. **Diffusion $S_{\text{new}}[i]$**: Disperses words across coordinates using coprime permutation stride $(5i + r) \bmod 16$ ($\gcd(5, 16) = 1$).

## 4. Domain Separation & Counter Injection
- Absorption uses $S[8] \oplus j$ (monotonic block counter) and $S[9] \oplus \text{"HCAABSOR"}$ (`0x4843414142534F52`).
- Output extraction uses $S[14] \oplus \text{"HCAOUTPU"}$ (`0x4843414F55545055`) and $S[15] \oplus q$ (monotonic squeeze counter).
- This separation prevents length-extension attacks, slide attacks, and cross-phase state collisions.

## 5. Endianness
All word-to-byte conversions use network byte order (big-endian). This ensures deterministic serialization regardless of host architecture (x86_64, aarch64, riscv64).
