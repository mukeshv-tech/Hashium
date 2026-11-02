# HCA-0.4 Research: Overview & Scope

## 1. Executive Summary & Objective

This document initiates **HCA-0.4 — Independent Cryptanalysis & Design Review** for the Hashium Custom Algorithm (HCA-0.1 / HCA-0.2 / HCA-0.3).

The primary objective of HCA-0.4 is **not** to assert security, but to conduct an unsparing, systematic investigation into the mathematical, structural, statistical, and operational properties of the HCA wide-pipe sponge construction.

> **CRITICAL RESEARCH CAVEAT:**
> Passing statistical tests (such as avalanche, NIST SP 800-22, or toy collision resistance) does **NOT** constitute proof of cryptographic security.
> HCA remains strictly an experimental research algorithm. It must **not** be recommended or used for passwords, authentication, signatures, disk encryption, or security-critical applications.

---

## 2. Research Classification Standards

Every assertion and finding throughout the `docs/hca/research/` reports is strictly categorized into one of four formalized epistemological classes:

1. **[MATHEMATICALLY ESTABLISHED]**: Rigorously proven by algebraic derivation, discrete mathematical identity, or formal structural definition.
2. **[EXPERIMENTALLY OBSERVED]**: Empirically measured via reproducible computational scripts, Monte Carlo trials, or statistical test suites.
3. **[HYPOTHESIS]**: Plausible theoretical reasoning or conjecture supported by structural analogy, but not yet formally proven or refuted.
4. **[UNKNOWN]**: Open research questions where existing analysis is insufficient to determine cryptographic boundaries.

---

## 3. Documents in the Research Package

The complete HCA-0.4 Independent Cryptanalysis Package consists of:

- [`overview.md`](file:///C:/Users/Mukesh/Hashium/docs/hca/research/overview.md): Scope, epistemological framework, and research structure.
- [`mixing-function-analysis.md`](file:///C:/Users/Mukesh/Hashium/docs/hca/research/mixing-function-analysis.md): 1024-bit state transformation, dependency graph, invertibility, and round properties.
- [`diffusion-analysis.md`](file:///C:/Users/Mukesh/Hashium/docs/hca/research/diffusion-analysis.md): Single-bit and multi-bit differential propagation, avalanche measurements, and bit independence.
- [`collision-analysis.md`](file:///C:/Users/Mukesh/Hashium/docs/hca/research/collision-analysis.md): Sponge capacity bounds, multi-collisions, length extension, and birthday search behavior.
- [`domain-separation-review.md`](file:///C:/Users/Mukesh/Hashium/docs/hca/research/domain-separation-review.md): Analysis of capacity tags $s_8$ and $s_9$, domain isolation, and counter wrapping bounds.
- [`variable-output-analysis.md`](file:///C:/Users/Mukesh/Hashium/docs/hca/research/variable-output-analysis.md): Extendable-output behavior (128 to 4096 bits), prefix consistency, and statistical distribution.
- [`findings.md`](file:///C:/Users/Mukesh/Hashium/docs/hca/research/findings.md): Comprehensive synthesis of identified structural weaknesses, ambiguities, open questions, and roadmap recommendations for HCA-0.5.

---

## 4. Reproducibility

All experiments cited in this research package can be reproduced using the standalone scripts in [`tests/research/`](file:///C:/Users/Mukesh/Hashium/tests/research/):
- `tests/research/exp1_mixing_invertibility.py`
- `tests/research/exp2_diffusion_avalanche.py`
- `tests/research/exp3_output_distribution.py`
- `tests/research/exp4_collision_domain.py`
