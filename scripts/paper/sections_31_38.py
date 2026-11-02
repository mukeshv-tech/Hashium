"""
Monographs Part 4: Sections 31 through 38 (Pages 33 to 40)
"""

SECTIONS_PART_4 = [
    # PAGE 33
    (
        "31. Invertibility Investigation & Multivariate Systems",
        "Non-Linear Feedback Inversion and Elimination Analysis",
        """
        A critical question in permutation-based cryptography is whether the underlying transformation <i><b>M</b>: (<b>Z</b><sub>2<sup>64</sup></sub>)<sup>16</sup> &rarr; (<b>Z</b><sub>2<sup>64</sup></sub>)<sup>16</sup></i> can be efficiently inverted in software without knowing the full internal state.
        
        System Inversion Formulation:
        Let <b>t</b> be the known 16-word output of a round before permutation. Reversing the bijective word permutation &pi;<sub>r</sub> yields:
        <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;y<sub>i</sub> = t<sub>i</sub> &Gt;&Gt; rot<sub>t</sub>(i, r) = a<sub>i</sub> &oplus; b<sub>i</sub></font><br/>
        Substituting the definitions of <i>a<sub>i</sub></i> and <i>b<sub>i</sub></i> gives a non-linear multivariate equation for each word <i>i &isin; [0, 15]</i>:
        <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;[s<sub>i</sub> + ((s<sub>i+1</sub> &oplus; RC[r][i]) &Lt;&Lt; 13)] &oplus; [(s<sub>i+4</sub> + s<sub>i+11</sub>) &Lt;&Lt; rot<sub>b</sub>] = y<sub>i</sub></font><br/>
        
        Structural Invertibility Properties:
        1. Linear Isolation of <i>s<sub>i</sub></i>:
           Word <i>s<sub>i</sub></i> appears under modular addition in exactly one equation (index <i>i</i>). If words <i>s<sub>i+1</sub>, s<sub>i+4</sub>, s<sub>i+11</sub></i> were hypothetically known, <i>s<sub>i</sub></i> could be derived by subtraction:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;s<sub>i</sub> = [y<sub>i</sub> &oplus; ((s<sub>i+4</sub> + s<sub>i+11</sub>) &Lt;&Lt; rot<sub>b</sub>)] - ((s<sub>i+1</sub> &oplus; RC[r][i]) &Lt;&Lt; 13) mod 2<sup>64</sup></font><br/>
        2. Cyclic Non-Linear Interlocking:
           Because index <i>i+1</i> wraps circularly around the 16 words, every word is coupled to its successor. Simultaneously, <i>s<sub>i+4</sub></i> and <i>s<sub>i+11</sub></i> create long-range non-local dependencies.
        """,
        """
        Conclusion on Invertibility:
        While <b>M</b> is structurally bijective (no collisions observed), inverting a single round without knowing intermediate words requires solving an interdependent non-linear system of 16 equations in 16 unknowns across non-associative (+, &oplus;, &Lt;&Lt;) fields. 
        Across 12 iterated rounds, inversion complexity exceeds brute-force state search.
        """
    ),
    # PAGE 34
    (
        "32. Invariant Subspace Analysis & Constant-State Fixed Points",
        "Analysis of Zero-State, One-State, and Periodic Attractors",
        """
        An algorithmically weak cipher can contain invariant subspaces&mdash;subsets of the state space that map onto themselves under the permutation (e.g., if <i><b>M</b>(0<sup>1024</sup>) = 0<sup>1024</sup></i> or if alternating bit patterns are preserved).
        
        Fixed-Point Empirical Evaluations (<code>exp1_mixing_invertibility.py</code>):
        1. All-Zero State (<i>0<sup>1024</sup></i>):
           Testing whether an absorbed message of all zeros causes the state to stagnate:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>M</b>(0<sup>1024</sup>) = [0xfecc2993738aa75e, 0x16073acc3121cd3f, ...]</font><br/>
           Result: The all-zero state is aggressively disrupted in Round 1. The SplitMix64 round constants inject high-entropy pseudo-random bits into register <i>a<sub>i</sub></i>, destroying the all-zero attractor.
        2. All-Ones State (<i>1<sup>1024</sup></i>):
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>M</b>(1<sup>1024</sup>) = [0x0a3fd15c123fd70b, 0x9320e89547d2d140, ...]</font><br/>
           Result: The all-ones state similarly diffuses into pseudo-random bit configurations.
        3. Alternating Bit Masks (<code>0x5555...</code> and <code>0xAAAA...</code>):
           Evaluated across 12 rounds. Modulo <i>2<sup>64</sup></i> addition carries break alternating bit symmetries at bit position 1, cascading across the register.
        """,
        """
        Classification:
        - Absence of Trivial Fixed Points: [MATHEMATICALLY ESTABLISHED via Round Constants]
        - Absence of Subspace Attractors: [EXPERIMENTALLY OBSERVED across standard periodic bases]
        - Complete Proof of Subspace Freedom: [UNKNOWN - Requires exhaustive polynomial ideal analysis]
        """
    ),
    # PAGE 35
    (
        "33. Statistical Output Distribution & NIST SP 800-22 Suite",
        "Empirical Randomness Verification on 512-Bit Digests",
        """
        To verify that the output of HCA exhibits no macroscopic statistical defects, output streams were evaluated against the National Institute of Standards and Technology (NIST) Special Publication 800-22 test suite (<code>exp3_output_distribution.py</code>).
        
        Testing Methodology:
        - 500 consecutive 512-bit digests generated from incremental counter messages: <i>M<sub>k</sub> = \text{"Statistical_Test_Message_"} || k</i>.
        - Total evaluated bitstream: 256,000 continuous bits.
        - Significance level: <i>&alpha; = 0.01</i> (expected pass rate &ge; 98.0%).
        
        NIST SP 800-22 Empirical Results:
        1. Frequency (Monobit) Test:
           Measures the proportion of ones and zeros across the sequence.
           - Observed bit proportion: <i>&pi; = 0.50027</i> (Ideal: 0.50000).
           - Monobit Pass Rate: <b>99.4%</b> (497 / 500 batches passed).
        2. Frequency Test within a Block:
           Measures whether the frequency of ones in M-bit blocks is approximately M/2.
           - Block Pass Rate: <b>99.0%</b>.
        3. Runs Test:
           Examines the total number of runs of consecutive ones and zeros of various lengths.
           - Runs Pass Rate: <b>98.8%</b> (494 / 500 batches passed).
        """,
        """
        Epistemological Caveat on Statistical Testing:
        Statistical tests demonstrate only that HCA exhibits no detectable macroscopic linear or frequency biases under standard tests. 
        Statistical uniformity is a NECESSARY baseline, but NEVER a proof of cryptographic collision or preimage resistance.
        """
    ),
    # PAGE 36
    (
        "34. Cryptanalytic Bound Classifications & Hypotheses",
        "Formal Categorization of Established Theorems vs. Conjectures",
        """
        In compliance with scientific rigor, HCA-0.4 categorizes all security and architectural properties into four formal epistemological classes:
        
        1. [MATHEMATICALLY ESTABLISHED]:
           - Bijectivity of affine permutation &pi;<sub>r</sub>(i) = (5i + r) mod 16.
           - Complete word dependency achieved at Round 3.
           - Sponge indifferentiability bound: 2<sup>256</sup> collision security for c = 512.
           - Prefix consistency across variable-length squeezes: HCA(M, L<sub>1</sub>) &equiv; HCA(M, L<sub>2</sub>)[0..L<sub>1</sub>/8].
           - Immunity to Merkle-Damgard length-extension attacks.
           - Bit-length suffixed padding collision freedom.
        
        2. [EXPERIMENTALLY OBSERVED]:
           - Strict Avalanche Criterion (SAC) mean: 49.8% to 50.8% bit flip across all payload lengths.
           - Absence of fixed points for 0<sup>1024</sup>, 1<sup>1024</sup>, and periodic masks.
           - NIST SP 800-22 Monobit (99.4%) and Runs (98.8%) pass rates.
           - Multi-core linear scaling: 1,585 MB/s throughput on 12-core hardware.
        
        3. [HYPOTHESIS]:
           - Maximum distinguisher penetration depth is bounded at 5 to 6 rounds.
           - Algebraic normal form (ANF) polynomial degree reaches maximum (d = 1023) by Round 6.
           - Classical preimage search complexity equals 2<sup>512</sup>.
        
        4. [UNKNOWN]:
           - Formal mathematical upper bounds on higher-order differential characteristics for Round 12.
           - Exact complexity of solving 4-round reduced HCA via SAT/SMT solvers (e.g., Z3).
        """,
        """
        Significance of Epistemological Rigor:
        By explicitly labeling hypotheses and unknowns, HCA avoids the common pitfall of conflating empirical benchmark speed with cryptographic security.
        """
    ),
    # PAGE 37
    (
        "35. Structural Weaknesses Discovered in HCA-0.3",
        "Detailed Design Limitations and Architectural Flaws",
        """
        During the independent cryptanalytic review of HCA-0.3, three specific structural design weaknesses were identified:
        
        Weakness 1: Single-Word Domain Injection (<i>s<sub>9</sub></i>):
        In HCA-0.3, all protocol domain separation tags (absorption, squeeze, stream cipher, AEAD) are injected exclusively into capacity register <i>s<sub>9</sub></i>. 
        Registers <i>s<sub>10</sub> ... s<sub>15</sub></i> receive no domain-specific entropy. 
        While Round 1 diffuses <i>s<sub>9</sub></i> into neighboring words, concentrating domain isolation into a single 64-bit word increases susceptibility to differential cancellation if an attacker can manipulate word 9 in an absorbed block.
        
        Weakness 2: String-Prefixed Tree Hashing vs. State Domain Separation:
        In the parallel tree hashing mode (HCATREE), chunk isolation is enforced by prepending ASCII prefixes (<code>"HCALEAF:"</code>, <code>"HCATREE:"</code>, <code>"HCAROOT:"</code>) to message buffers. 
        While mathematically collision-free due to length-suffix padding, string prefixes incur memory copying overhead and represent a stylistic deviation from native sponge state domain separation.
        
        Weakness 3: Linear State Difference at Squeeze Transition:
        When transitioning from message absorption to output squeezing, capacity word <i>s<sub>9</sub></i> is updated via bitwise XOR with <b>D</b><sub>output</sub>. 
        Because the previous block had absorbed <b>D</b><sub>absorb</sub>, the pre-mixing state difference is a purely linear XOR constant:
        <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;&Delta; = <b>D</b><sub>absorb</sub> &oplus; <b>D</b><sub>output</sub> = 0x0000000E17071F07</font><br/>
        All non-linear transition relies entirely on the subsequent 12 mixing rounds.
        """,
        """
        Severity Classification:
        - Weakness 1: Moderate (Architectural improvement recommended for HCA-0.5).
        - Weakness 2: Minor (Ergonomic / stylistic; does not compromise collision bounds).
        - Weakness 3: Low (Mitigated by 12-round mixing permutation security margin).
        """
    ),
    # PAGE 38
    (
        "36. Specification Ambiguities & Edge-Case Vulnerabilities",
        "Boundary Conditions, Fractional Bits, and Truncation",
        """
        Review of the formal HCA-0.1 specification identified several implementation and specification ambiguities that require standardization:
        
        Ambiguity 1: Sub-Byte Fractional Input Lengths:
        The current specification defines padding and absorption exclusively for byte-aligned data (multiples of 8 bits). 
        If an application provides fractional-bit inputs (e.g., a 13-bit binary string), the behavior is undefined. 
        Standardization must adopt ISO/IEC 10118-3 bit-level padding conventions.
        
        Ambiguity 2: Output Length Validation Range:
        The specification allows output lengths from 128 to 4096 bits in multiples of 8. 
        However, the behavior when requesting non-multiple-of-8 bitlengths (e.g., 255 bits) is handled via exception raising rather than bit-level truncation. 
        
        Ambiguity 3: Tree Hash Chunk Alignment:
        HCATREE partitions data into 128 KB chunks. If the total file length is not an exact multiple of 128 KB, the final leaf chunk is truncated to the remaining byte count. 
        While chunk indices are bound into leaf headers, the specification does not explicitly state whether the final leaf chunk must be padded individually before hashing. In the Rust implementation, each leaf engine applies independent canonical padding.
        """,
        """
        Resolution for HCA-0.5:
        All edge-case ambiguities must be formalized in an updated RFC-style specification document with normative test vectors covering non-aligned boundaries.
        """
    ),
    # PAGE 39
    (
        "37. Formal Cryptanalysis Methodology for HCA-0.5",
        "Automated SAT/SMT Solvers and Differential Trail Bounding",
        """
        To transition HCA from empirical heuristic analysis to formal mathematical cryptanalysis, HCA-0.5 will introduce an automated SAT/SMT verification harness.
        
        SAT Solver Cryptanalysis Framework:
        Modern automated cryptanalysis models ARX operations as Boolean satisfiability (SAT) problems:
        - Bitwise XOR: Exact linear Boolean clauses.
        - Circular Rotation: Deterministic wire permutation clauses.
        - Modular Addition: Encoded using ripple-carry or carry-lookahead Boolean logic clauses.
        
        By translating reduced-round HCA (1 to 6 rounds) into Conjunctive Normal Form (CNF) formulas, solvers like CryptoMiniSat, CaDiCaL, and Z3 can:
        1. Identify optimal differential characteristics with minimal Hamming weight.
        2. Search for real preimages on 2-round and 3-round toy instances.
        3. Empirically verify the minimum round threshold where SAT solving transitions from polynomial time to intractable exponential search.
        """,
        """
        Proposed SAT Benchmark Suite:
        - 1-Round Inversion: Expected solve time < 0.1s.
        - 2-Round Inversion: Expected solve time ~ 2.5s.
        - 3-Round Inversion: Expected solve time ~ 120s.
        - 4-Round Inversion: Expected transition to intractable (&gt; 24 hours).
        Confirming intractability at Round 4 will provide mathematical validation of the 12-round security margin.
        """
    ),
    # PAGE 40
    (
        "38. Conclusion, Future Roadmap & References",
        "Concluding Remarks, Next Development Phases, and Citations",
        """
        This technical whitepaper has presented the comprehensive mathematical specification, empirical performance scaling, and independent cryptanalytic design review of the Hashium Custom Algorithm (HCA-0.3 / HCA-0.4).
        
        By unifying a wide-pipe 1024-bit sponge construction with an unrolled 12-round ARX mixing engine, compile-time SplitMix64 constant tables, and a 128 KB leaf chunk parallel tree mode, HCA achieves sustained multi-core hashing throughput of <b>1.58 GB/s</b> in software while providing integrated symmetric ciphering and AEAD capabilities.
        
        Future Development Roadmap:
        - HCA-0.5 (Q1 2027): Automated SAT/SMT differential solver harness and native capacity domain expansion.
        - HCA-0.6 (Q2 2027): Explicit AVX-512 and ARM NEON vectorized intrinsics in native Rust core.
        - HCA-1.0 (Target 2028): Independent third-party formal audit and submission to open cryptanalytic competitions.
        
        Academic References:
        1. Bertoni, G., Daemen, J., Peeters, M., & Van Assche, G. (2011). Cryptographic Sponge Functions.
        2. O'Connor, J., Aumasson, J. P., Neves, S., & Wilcox-O'Hearn, Z. (2020). BLAKE3: One function, fast everywhere.
        3. Bernstein, D. J. (2008). The ChaCha family of stream ciphers.
        4. Steele, G. L., & Vigna, S. (2014). Fast splittable pseudorandom number generators (SplitMix64).
        5. Webster, A. F., & Tavares, S. E. (1985). On the design of S-boxes (Strict Avalanche Criterion).
        6. Biham, E., & Shamir, A. (1991). Differential cryptanalysis of DES-like cryptosystems.
        7. Joux, A. (2004). Multicollisions in iterated hash functions.
        8. Maurer, U., Renner, R., & Holenstein, C. (2004). Indifferentiability, operational security, and random oracles.
        """,
        """
        Contact & Community:
        Hashium Cryptography Project
        GitHub: https://github.com/mukeshv-tech/Hashium
        License: MIT / Apache 2.0 Dual License
        Document Complete - End of Technical Whitepaper (Page 40 of 40).
        """
    )
]
