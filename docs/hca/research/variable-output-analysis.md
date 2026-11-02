# HCA-0.4 Research: Variable-Length Output & Statistical Analysis

## 1. Variable Output Generation (128 to 4096 bits)

HCA functions as an Extendable-Output Function (XOF), allowing output digests to be sized from 128 bits (16 bytes) to 4096 bits (512 bytes) in multiples of 8.

The extraction pipeline operates as:
1. Extract first 64 bytes from rate words $s_0 \dots s_7$.
2. If more bytes are required:
   - Mix state: $\mathcal{S} \leftarrow \mathcal{M}(\mathcal{S})$.
   - Extract next 64 bytes from $s_0 \dots s_7$.
3. Truncate concatenated stream to requested bit length $L/8$.

---

## 2. Mathematical Prefix-Consistency Verification

- **[MATHEMATICALLY ESTABLISHED]**: For any valid output lengths $L_1 \le L_2$:
$$\text{HCA}(M, L_1) \equiv \text{HCA}(M, L_2)[0 \dots L_1/8]$$
This property is formally proven by the sequential extraction order of rate words and is empirically verified across all test suites (`tests/test_hca_properties.py`).

---

## 3. Statistical Distribution Testing (NIST SP 800-22 Suite)

Evaluated across 500 consecutive 512-bit digests (256,000 total bits) generated from sequential counter payloads using `tests/research/exp3_output_distribution.py`:

| Statistical Metric | Observed Value | Ideal Theoretical Value | Pass Rate ($\alpha = 0.01$) | Classification |
|---|---|---|---|---|
| **Overall Proportion of 1s ($\pi$)** | **0.50027** | 0.50000 | — | [EXPERIMENTALLY OBSERVED] |
| **NIST Frequency (Monobit) Test** | $\mu_p = 0.512$ | Uniform in $[0, 1]$ | **99.4%** | [EXPERIMENTALLY OBSERVED] |
| **NIST Runs Test** | $\mu_p = 0.498$ | Uniform in $[0, 1]$ | **98.8%** | [EXPERIMENTALLY OBSERVED] |

- **[EXPERIMENTALLY OBSERVED]**: The output bitstream exhibits pseudo-random distribution matching independent identically distributed (i.i.d.) Bernoulli(0.5) trials.

---

## 4. Epistemological Limitations of Statistical Testing

- **[CRITICAL CAVEAT]**:
  Statistical tests (including NIST SP 800-22, Dieharder, and TestU01) measure only macroscopic uniformity and the absence of coarse linear/spectral biases.
  A cipher or hash function can pass all NIST statistical tests with a 100% score while being completely vulnerable to:
  - Algebraic attacks (e.g., low degree polynomial solvers).
  - Side-channel leakage.
  - Chosen-message differential collisions.
  - Backdoored key schedules.
  
  Therefore, passing NIST statistical tests must **never** be cited as evidence of cryptographic security.
