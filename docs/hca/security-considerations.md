# HCA-0.1 Security Considerations

## 1. Experimental Status
HCA-0.1 is an **experimental, unverified** algorithm. It is not an established cryptographic primitive (such as SHA-2, SHA-3, BLAKE3, or Ascon).

## 2. Inappropriate Uses
HCA-0.1 must **NOT** be used for:
- Password hashing or credential verification (use Argon2id or bcrypt).
- Digital signatures or public-key cryptography.
- Integrity verification of critical software or security patches.
- Cryptographic authentication or HMAC in production systems.
- Proof-of-work or consensus mechanisms.

## 3. Potential Vulnerabilities & Open Questions
1. **Bijectivity of Permutation**: The round function has not been mathematically proven to be a permutation (a bijection over $\{0, 1\}^{1024}$). If non-bijective, state entropy could degrade across multiple rounds or long message absorptions.
2. **Rotational & Differential Cryptanalysis**: Although dynamic rotations are employed, formal upper bounds on differential characteristics and linear hulls have not been computed.
3. **Algebraic Degree & S-box-free Design**: The non-linearity is derived solely from modular addition and bitwise XOR/rotations (ARX-like). Higher-order differential attacks have not been studied on this specific construction.
4. **Side-Channel Analysis**: The reference and native implementations prioritize constant-time execution for native wrapping operations on 64-bit platforms, but no formal microarchitectural leakage analysis has been conducted.

## 4. Safe Exploration
This primitive is solely provided under `hashium.experimental.hca` for academic exploration, differential analysis experimentation, and educational benchmarking.
