# HCA-0.4 Research: Domain Separation & State Injection Review

## 1. Domain Constants Analysis

HCA defines four 64-bit domain constants injected into capacity word $s_9$:
- $\mathcal{D}_{\text{absorb}} = \mathtt{0x4843414142534F52}$ (`"HCAABSOR"`)
- $\mathcal{D}_{\text{output}} = \mathtt{0x4843414F55545055}$ (`"HCAOUTPU"`)
- $\mathcal{D}_{\text{cipher}} = \mathtt{0x4843414349504852}$ (`"HCACIPHR"`)
- $\mathcal{D}_{\text{aead}} = \mathtt{0x4843414145414400}$ (`"HCAAEAD\0"`)

### 1.1 Pairwise Hamming Distances
- **[MATHEMATICALLY ESTABLISHED]**:
  - $\Delta_H(\mathcal{D}_{\text{absorb}}, \mathcal{D}_{\text{output}}) = 18$ bits.
  - $\Delta_H(\mathcal{D}_{\text{absorb}}, \mathcal{D}_{\text{cipher}}) = 13$ bits.
  - $\Delta_H(\mathcal{D}_{\text{absorb}}, \mathcal{D}_{\text{aead}}) = 14$ bits.
  All domain constants are separated by at least 13 non-adjacent bit positions, preventing low-weight linear cancelation.

---

## 2. Block Counter ($s_8$) Mechanics

During absorption, capacity word $s_8$ is updated as:
$$s_8 \leftarrow s_8 \oplus j, \quad j \in [0, N-1]$$

### 2.1 Counter Wrapping Analysis
- **[MATHEMATICALLY ESTABLISHED]**: The block counter $j$ is a 64-bit unsigned integer. Wrapping back to $j = 0$ requires processing $2^{64}$ blocks of 64 bytes each:
$$\text{Data Volume} = 2^{64} \times 64\text{ bytes} = 2^{70}\text{ bytes} = 1\text{ Zettabyte}$$
This volume is physically unachievable under classical computation, meaning $s_8$ never wraps in practice.

---

## 3. Potential Problematic Design Choices & Weaknesses

- **[STRUCTURAL WEAKNESS / SPECIFICATION AMBIGUITY]**:
  1. **Single-Word Domain Injection ($s_9$ only):**
     Domain constants are injected solely into word $s_9$. The remaining capacity words $s_{10} \dots s_{15}$ do not receive domain separation. While Round 1 spreads $s_9$ across adjacent words, injecting domain constants across multiple capacity words would provide greater algebraic resilience.
  2. **Sequential XOR Interaction in Squeeze:**
     During the transition from absorption to squeeze, capacity word $s_9$ is updated via:
     $$s_9 \leftarrow s_9 \oplus \mathcal{D}_{\text{output}}$$
     Because the previous state had absorbed $\mathcal{D}_{\text{absorb}}$ in $s_9$ during the final block, the effective difference applied to $s_9$ at squeeze transition is:
     $$\Delta = \mathcal{D}_{\text{absorb}} \oplus \mathcal{D}_{\text{output}} = \mathtt{0x0000000E17071F07}$$
     This transition is linear. The non-linearity relies strictly on the subsequent 12-round mixing step.
  3. **Lack of Tree Hash Formal Domain in $s_9$:**
     In the parallel tree hashing mode (`tree.rs`), domain separation is achieved by prepending ASCII prefixes to the message (`"HCALEAF:"`, `"HCATREE:"`, `"HCAROOT:"`) rather than injecting dedicated tree domain constants into $s_9$. While functionally collision-free due to length-suffix padding, using state-level domain constants in $s_9$ would be cleaner and eliminate string parsing overhead.
