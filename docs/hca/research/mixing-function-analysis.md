# HCA-0.4 Research: Mixing Function & State Transformation Analysis

## 1. Overview of the 1024-Bit Transformation

The core permutation $\mathcal{M}(\mathcal{S})$ operates on sixteen 64-bit unsigned integers:
$$\mathcal{S} = [s_0, s_1, \dots, s_{15}] \in (\mathbb{Z}_{2^{64}})^{16}$$

Each round $r \in [0, 11]$ consists of an unrolled ARX intra-round transformation producing intermediate vector $\mathbf{t} = [t_0, \dots, t_{15}]$, followed by an inter-round word permutation $\pi_r$:
$$a_i = s_i + \left((s_{(i+1) \bmod 16} \oplus \mathbf{RC}[r][i]) \lll 13\right) \pmod{2^{64}}$$
$$b_{\text{sum}} = s_{(i+4) \bmod 16} + s_{(i+11) \bmod 16} \pmod{2^{64}}$$
$$\text{rot}_b = (7i + 3r) \bmod 64, \quad b_i = b_{\text{sum}} \lll \text{rot}_b$$
$$\text{rot}_t = (11i + 7r + 1) \bmod 64, \quad t_i = (a_i \oplus b_i) \lll \text{rot}_t$$
$$\mathcal{S}_{\text{new}}[i] = t_{(5i + r) \bmod 16}$$

---

## 2. Invertibility Investigation

### 2.1 Inter-Round Word Permutation Bijectivity
- **[MATHEMATICALLY ESTABLISHED]**: The mapping $\pi_r(i) = (5i + r) \bmod 16$ is a permutation on $\mathbb{Z}_{16}$ for every round $r$. Because $\gcd(5, 16) = 1$, the multiplicative inverse $5^{-1} \equiv 13 \pmod{16}$ exists uniquely. Hence, $\pi_r$ is invertible:
$$\pi_r^{-1}(j) = 13(j - r) \bmod 16$$
No state words are destroyed or duplicated during word permutation.

### 2.2 Intra-Round System Invertibility
- **[MATHEMATICALLY ESTABLISHED]**: Inverting a single round given intermediate output $\mathbf{t}$ requires solving the system:
$$y_i = t_i \ggg \text{rot}_t = a_i \oplus b_i$$
$$(s_i + \text{Rot}(s_{i+1} \oplus \mathbf{RC}[r][i], 13)) \oplus \text{Rot}(s_{i+4} + s_{i+11}, \text{rot}_b) = y_i$$
Notice that word $s_i$ appears linearly under modular addition in exactly one equation (index $i$). If words $s_{i+1}, s_{i+4}, s_{i+11}$ are known, $s_i$ can be uniquely recovered via subtraction:
$$s_i = \left(y_i \oplus \text{Rot}(s_{i+4} + s_{i+11}, \text{rot}_b)\right) - \text{Rot}(s_{i+1} \oplus \mathbf{RC}[r][i], 13) \pmod{2^{64}}$$
However, because indices $(i+1, i+4, i+11) \bmod 16$ form a cyclic dependency network across all 16 equations, the system cannot be solved by simple back-substitution without guessing intermediate words or using algebraic SAT/Gröbner basis solvers.

- **[HYPOTHESIS]**: The permutation $\mathcal{M}$ is bijective over $(\mathbb{Z}_{2^{64}})^{16}$, meaning there are no internal collision states $S_1 \ne S_2$ where $\mathcal{M}(S_1) = \mathcal{M}(S_2)$. However, an efficient algebraic inverse algorithm has not been constructed.

---

## 3. Dependency Graph & Word Diffusion

Tracking the set of input words that contribute to each state word across rounds:

| Round | Average Input Words Depended On | Min Words | Max Words | Classification |
|:---:|:---:|:---:|:---:|:---:|
| **0** (Initial) | 1.0 | 1 | 1 | [MATHEMATICALLY ESTABLISHED] |
| **1** | 4.0 | 4 | 4 | [MATHEMATICALLY ESTABLISHED] |
| **2** | 11.0 | 11 | 11 | [MATHEMATICALLY ESTABLISHED] |
| **3** | **16.0** | **16** | **16** | [MATHEMATICALLY ESTABLISHED] |
| **4 .. 12** | **16.0** | **16** | **16** | [MATHEMATICALLY ESTABLISHED] |

- **[MATHEMATICALLY ESTABLISHED]**: By Round 3, every single output word depends algebraically on all sixteen input words. Complete full-state word dependency is attained in 25% of the total round budget.

---

## 4. Invariant Subspaces and Fixed Points

- **[EXPERIMENTALLY OBSERVED]**:
  - **All-zero state ($0^{1024}$):** $\mathcal{M}(0^{1024}) \ne 0^{1024}$. Word $s_0$ outputs `0xfecc2993738aa75e`. The static SplitMix64 round constants inject non-zero entropy at every step, destroying zero-state fixed points.
  - **All-ones state ($1^{1024}$):** $\mathcal{M}(1^{1024}) \ne 1^{1024}$. Word $s_0$ outputs `0x0a3fd15c123fd70b`.

- **[UNKNOWN]**: Whether non-trivial invariant subspaces or rotational fixed points exist under specific multi-word periodic structures.
