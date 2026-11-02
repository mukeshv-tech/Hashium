"""
Monographs Part 2: Sections 11 through 20 (Pages 13 to 22)
"""

SECTIONS_PART_2 = [
    # PAGE 13
    (
        "11. Canonical Padding & Block Alignment Invariants",
        "Bit-Length Suffix Encoding and Ambiguity Prevention",
        """
        In any cryptographic hash function operating on discrete block boundaries, the padding rule must establish a strict bijection between arbitrary unpadded byte sequences and valid padded block sequences. If two distinct inputs <i>M<sub>1</sub> &ne; M<sub>2</sub></i> can result in the same padded blocks, trivial hash collisions occur.
        
        HCA specifies a deterministic, unambiguous bit-length suffix padding scheme operating on 64-byte (512-bit) block multiples.
        
        Formal Padding Specification:
        Let <i>M</i> be an arbitrary input message of byte length <i>|M| &ge; 0</i>.
        1. Mandatory Delimiter: A single byte with value <code>0x80</code> (binary <code>10000000</code>) is appended to <i>M</i>. This unequivocally marks the termination of message bytes.
        2. Zero-Fill Alignment: <i>k &ge; 0</i> zero bytes (<code>0x00</code>) are appended, where <i>k</i> is the smallest non-negative integer satisfying:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;(|M| + 1 + k + 8) &equiv; 0 mod 64</font><br/>
        3. Message Length Binding: An 8-byte (64-bit) unsigned integer encoding the total bit length of the unpadded message in network big-endian order is appended:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>L</b> = (|M| &times; 8)<sub>BE64</sub></font><br/>
           
        Theorem 2 (Padding Collision Freedom):
        No two distinct messages <i>M<sub>1</sub> &ne; M<sub>2</sub></i> can produce identical padded byte sequences <i>P(M<sub>1</sub>) = P(M<sub>2</sub>)</i>.
        
        Proof:
        Case 1: <i>|M<sub>1</sub>| &ne; |M<sub>2</sub>|</i>. The final 8 bytes of <i>P(M<sub>1</sub>)</i> and <i>P(M<sub>2</sub>)</i> encode <i>|M<sub>1</sub>| &times; 8</i> and <i>|M<sub>2</sub>| &times; 8</i> respectively. Because integer encoding is unique, the last 8 bytes differ, so <i>P(M<sub>1</sub>) &ne; P(M<sub>2</sub>)</i>.
        Case 2: <i>|M<sub>1</sub>| = |M<sub>2</sub>|</i>, but <i>M<sub>1</sub> &ne; M<sub>2</sub></i>. Because <i>|M<sub>1</sub>| = |M<sub>2</sub>|</i>, the padding lengths <i>k<sub>1</sub> = k<sub>2</sub></i> and suffix lengths are identical. Therefore, the difference between <i>M<sub>1</sub></i> and <i>M<sub>2</sub></i> is preserved in the first <i>|M<sub>1</sub>|</i> bytes of the block sequence, ensuring <i>P(M<sub>1</sub>) &ne; P(M<sub>2</sub>)</i>.
        """,
        """
        Boundary Padding Examples:
        - Empty Message (|M| = 0):
          1 byte (0x80) + 55 zero bytes + 8 bytes (0x00..00) = Exactly 64 bytes (1 block).
        - Block Boundary Minus 9 (|M| = 55):
          55 bytes + 1 byte (0x80) + 0 zero bytes + 8 bytes length = Exactly 64 bytes (1 block).
        - Block Boundary Minus 8 (|M| = 56):
          56 bytes + 1 byte (0x80) + 63 zero bytes + 8 bytes length = Exactly 128 bytes (2 blocks).
        - Full Block (|M| = 64):
          64 bytes + 1 byte (0x80) + 55 zero bytes + 8 bytes length = Exactly 128 bytes (2 blocks).
        """
    ),
    # PAGE 14
    (
        "12. Absorption Loop Mechanics & Capacity Barrier",
        "Zero-Copy Block Injection and Invariant State Transition",
        """
        The absorption phase is the core mechanism through which message data enters the HCA wide-pipe state. In accordance with sponge theory, data is absorbed exclusively into the rate portion of the state, preserving the capacity partition as an untouched cryptographic barrier.
        
        Absorption Cycle for Block <i>B<sub>j</sub></i> (index <i>j &isin; [0, N-1]</i>):
        1. Zero-Copy Pointer Word Decoding:
           The 64-byte block <i>B<sub>j</sub></i> is decoded as eight 64-bit big-endian words <i>W<sub>0</sub> ... W<sub>7</sub></i>:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;W<sub>k</sub> = DecodeBE64(B<sub>j</sub>[8k ... 8k + 7])</font><br/>
           In HCA-0.3, this operation is executed via direct pointer casting in Rust (<code>*const [u8; 8]</code>), avoiding dynamic vector allocations and eliminating array bounds checks during hot loops.
        2. Rate XOR Injection:
           Words <i>W<sub>0</sub> ... W<sub>7</sub></i> are XORed into rate registers <i>s<sub>0</sub> ... s<sub>7</sub></i>:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>S</b>[k] &larr; <b>S</b>[k] &oplus; W<sub>k</sub>, &forall; k &isin; [0, 7]</font><br/>
        3. Monotonic Block Index Binding:
           To prevent block relocation and circular permutation slide attacks, the 64-bit block index <i>j</i> is XORed into capacity word <i>s<sub>8</sub></i>:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>S</b>[8] &larr; <b>S</b>[8] &oplus; j</font><br/>
        4. Domain Separation Injection:
           Capacity word <i>s<sub>9</sub></i> is XORed with the static absorption domain constant:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>S</b>[9] &larr; <b>S</b>[9] &oplus; <b>D</b><sub>absorb</sub>, <b>D</b><sub>absorb</sub> = 0x4843414142534F52</font><br/>
        5. Permutation Application:
           The full 1024-bit state undergoes 12 rounds of non-linear mixing:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>S</b> &larr; <b>M</b>(<b>S</b>)</font><br/>
        """,
        """
        The Capacity Barrier Principle:
        Notice that capacity words s<sub>10</sub> ... s<sub>15</sub> receive no direct input injection. Because the capacity is 512 bits wide, an adversary attempting to control the entire state <b>S</b> must solve a constrained system across 512 unobserved, non-linearly diffused bits. 
        This structural barrier prevents state-reconstruction attacks and guarantees that differential trails injected into the rate words are scrambled before subsequent blocks are absorbed.
        """
    ),
    # PAGE 15
    (
        "13. Squeeze Phase & Arbitrary Variable Output Derivation",
        "Domain Squeeze Transitions and Multi-Block Output Expansion",
        """
        Once all message blocks have been absorbed, HCA enters the squeeze phase to generate the final digest. Unlike fixed-output hash functions (such as SHA-256), sponge functions act as Extendable-Output Functions (XOFs), capable of generating arbitrary output lengths from 128 bits up to 4096 bits.
        
        Squeeze Phase Execution:
        1. Domain Separation Squeeze Transition:
           Before any output bits are extracted, capacity word <i>s<sub>9</sub></i> is updated with the output domain tag, followed by an execution of the 12-round mixing permutation:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>S</b>[9] &larr; <b>S</b>[9] &oplus; <b>D</b><sub>output</sub>, <b>D</b><sub>output</sub> = 0x4843414F55545055</font><br/>
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>S</b> &larr; <b>M</b>(<b>S</b>)</font><br/>
           This transition acts as a one-way mathematical ratchet. Once the output domain is injected, it is computationally infeasible to invert <i><b>M</b>(<b>S</b>)</i> to recover the pre-squeeze state or deduce previously absorbed message blocks.
        2. Rate Extraction:
           The first 512 bits (64 bytes) of output are extracted directly from rate words <i>s<sub>0</sub> ... s<sub>7</sub></i> encoded as big-endian bytes:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;Block<sub>out</sub> = EncodeBE64(s<sub>0</sub>) || EncodeBE64(s<sub>1</sub>) || ... || EncodeBE64(s<sub>7</sub>)</font><br/>
        3. Multi-Block Squeeze Expansion:
           If the requested output length <i>L</i> exceeds 64 bytes (e.g., 1024 bits = 128 bytes, or 4096 bits = 512 bytes):
           - Consecutive 64-byte blocks are extracted by iteratively mixing the state: <i><b>S</b> &larr; <b>M</b>(<b>S</b>)</i> and reading out <i>s<sub>0</sub> ... s<sub>7</sub></i>.
           - The concatenated byte stream is truncated to exactly <i>L/8</i> bytes.
        """,
        """
        Prefix Consistency Invariant:
        In HCA-0.3, the output stream satisfies the sponge prefix consistency property:
        For any output lengths L<sub>1</sub> < L<sub>2</sub>, the L<sub>1</sub>-bit digest is an exact prefix of the L<sub>2</sub>-bit digest:
        <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;HCA(M, L<sub>1</sub>) = HCA(M, L<sub>2</sub>)[0 ... L<sub>1</sub>/8]</font><br/>
        This property is verified systematically across our test suite via Hypothesis property testing.
        """
    ),
    # PAGE 16
    (
        "14. Scalable Multi-Core Tree Hashing (HCATREE)",
        "Deterministic Binary Tree Topology and Parallel Decomposition",
        """
        Sequential hash functions are fundamentally bottlenecked on modern hardware: regardless of whether a server possesses 8, 32, or 128 CPU cores, a serial sponge can execute on only one core at any given microsecond.
        
        To unlock the full compute potential of modern multicore processors, HCA defines <b>HCATREE</b>, a deterministic binary tree hashing mode that parallelizes execution across arbitrary payloads.
        
        HCATREE Algorithmic Specification:
        1. Threshold Evaluation:
           If message byte length <i>|M| < 256 KB</i>, sequential single-pass HCA is retained to avoid thread scheduling latency.
        2. Chunk Partitioning:
           For <i>|M| &ge; 256 KB</i>, the message is partitioned into contiguous leaf chunks of size <i><b>C</b> = 128 KB</i>:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;M = C<sub>0</sub> || C<sub>1</sub> || ... || C<sub>N-1</sub>, N = &lceil; |M| / <b>C</b> &rceil;</font><br/>
        3. Independent Parallel Leaf Processing:
           Each chunk <i>k &isin; [0, N-1]</i> is hashed concurrently by worker threads using an isolated HCA-512 engine with a unique leaf domain header:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;Header<sub>k</sub> = "HCALEAF:" || (k)<sub>BE64</sub></font><br/>
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;LeafNode<sub>k</sub> = HCA-512(Header<sub>k</sub> || C<sub>k</sub>)</font><br/>
        4. Recursive Binary Tree Reduction:
           The resulting array of 64-byte leaf digests is reduced pairwise until a single root digest is reached:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;ParentNode = HCA-512("HCATREE:" || LeftChild || RightChild)</font><br/>
        5. Root Length Binding:
           The final root digest is bound to the total message length and squeezed to the user's requested output bit length:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;FinalDigest = HCA-Out("HCAROOT:" || RootNode || (|M|)<sub>BE64</sub>)</font><br/>
        """,
        """
        Tree Hash Security Invariants:
        - Domain Separation: Leaf headers ("HCALEAF:"), internal nodes ("HCATREE:"), and the root node ("HCAROOT:") utilize distinct ASCII prefixes, preventing tree-node confusion attacks.
        - Chunk Index Binding: Chunk index k is explicitly bound into each leaf, preventing chunk transposition or reordering attacks.
        - Length Binding: Total message byte length |M| is absorbed into the root node, preventing length-manipulation collisions between messages that share identical leaf prefixes.
        """
    ),
    # PAGE 17
    (
        "15. Leaf Chunk Sizing & Cache Micro-Architecture",
        "Cache Residency, Memory Bus Saturation, and Chunk Sizing",
        """
        The choice of leaf chunk size <i><b>C</b></i> in tree hashing is the paramount performance parameter determining real-world throughput on x86_64 and ARM64 processors.
        
        During development of HCA, three candidate chunk sizes were benchmarked across high-scale payloads (10 MB to 500 MB):
        1. 16 KB Leaf Chunks (HCA-0.2 Prototype):
           - Pros: Fits comfortably in 32 KB L1 Data Cache.
           - Cons: For large files (e.g., 100 MB = 6,400 chunks), creating and synchronizing 6,400 Rayon tasks generated excessive thread scheduling and binary tree reduction passes, throttling peak throughput to ~350 MB/s.
        2. 64 KB Leaf Chunks:
           - Pros: Reduced task count by 4x; increased throughput to ~540 MB/s.
           - Cons: Still incurred noticeable thread synchronization overhead on payloads > 50 MB.
        3. 128 KB Leaf Chunks (HCA-0.3 Standard):
           - Pros: Perfectly matches modern L2 cache allocations (typically 512 KB to 1 MB per core). For a 100 MB buffer, this yields exactly 800 chunks&mdash;an optimal workload distribution for a 12-to-16 core thread pool.
           - Result: Sustained throughput escalated to <b>1,585 MB/s</b>.
        """,
        """
        Micro-Architectural Cache Analysis:
        In 128 KB chunk mode, an entire leaf chunk occupies 2,048 absorption blocks (each 64 bytes). 
        When a worker thread absorbs a 128 KB chunk:
        - The entire slice remains resident in high-speed L2 CPU cache throughout the 2,048 absorption cycles.
        - Memory bus traffic occurs solely during initial sequential prefetching.
        - Intermediate 64-byte leaf digests are written directly back to cache, eliminating DRAM write latency.
        """
    ),
    # PAGE 18
    (
        "16. Rayon Work-Stealing & Thread Scheduling",
        "Multi-Thread Concurrency and Worker Pool Topology",
        """
        To orchestrate parallel execution across arbitrary numbers of CPU cores without lock contention, HCA integrates Rayon, Rust's premier data-parallelism framework.
        
        Rayon implements a work-stealing thread scheduler based on the Cilk model:
        - A fixed thread pool is instantiated with one worker thread per available logical CPU core.
        - When an input slice is divided into chunks via <code>data.chunks(LEAF_CHUNK_SIZE)</code>, tasks are pushed onto local worker deques.
        - Idle threads steal tasks from the back of busy workers' deques, ensuring optimal load balancing regardless of OS thread preemption or non-uniform memory access (NUMA) topologies.
        
        Lock-Free Tree Reduction:
        The pairwise binary tree reduction is executed via <code>par_chunks(2)</code>:
        <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;while current_nodes.len() &Gt; 1 {<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;current_nodes = current_nodes.par_chunks(2).map(...).collect();<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;}</font><br/>
        This reduction proceeds in <i>log<sub>2</sub>(N)</i> stages. For a 100 MB file (800 leaf nodes), the tree requires only 10 reduction stages, executing in under 0.8 milliseconds total reduction time.
        """,
        """
        System Performance Characteristics:
        - Core Utilization: Scales across all 12 logical cores on test workstations, achieving near-linear multi-core CPU saturation during large hashing passes.
        - Thread Safety: Rust's borrow checker guarantees that sub-slice references are read-only and memory-safe across concurrent threads without mutexes or atomic locks.
        """
    ),
    # PAGE 19
    (
        "17. Python ABI3 Native Bindings & Zero-Cost GIL Release",
        "PyO3 Architecture and Multi-Threaded Interoperability",
        """
        A notorious bottleneck in high-performance Python computing is the Global Interpreter Lock (GIL). Because the CPython runtime is not thread-safe, concurrent Python threads cannot execute bytecode simultaneously on multiple CPU cores.
        
        To overcome this limitation, HCA compiles its core Rust engine into a native C-extension using PyO3 and the stable Python ABI (ABI3).
        
        Zero-Cost GIL Release Mechanism:
        When Python calls <code>hca_parallel(data, output_bits)</code>, the PyO3 wrapper immediately releases the GIL before spawning Rayon worker threads:
        <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;#[pyfunction]<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;pub fn hca_parallel(py: Python, data: &[u8], output_bits: usize) -> PyResult&Lt;...&Gt; {<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;let result = py.allow_threads(|| tree::tree_hash(data, output_bits))?;<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ok(PyBytes::new(py, &result))<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;}</font><br/>
        
        Significance of <code>py.allow_threads</code>:
        1. Real Hardware Concurrency: Rayon threads execute native compiled Rust code across all available CPU cores with zero Python interpreter overhead.
        2. Host Application Responsiveness: Other Python threads in the host application continue running concurrently without being blocked by large hashing passes.
        3. ABI3 Stability: The resulting compiled wheel is forward-compatible across all Python versions from 3.8 to 3.14+ without recompilation.
        """,
        """
        Memory Zero-Copy Invariants:
        The Python binding accepts any object supporting the Python Buffer Protocol (bytes, bytearray, or memoryview). 
        Data is passed by raw pointer reference directly into Rust slices, preventing unnecessary multi-megabyte buffer copies between Python and Rust memory spaces.
        """
    ),
    # PAGE 20
    (
        "18. Symmetric Stream Encryption Duplex Construction",
        "Stateful Keystream Generation and Counter Synchronization",
        """
        The mathematical flexibility of the sponge construction permits stateful duplexing, allowing HCA to serve as a high-speed symmetric stream cipher without introducing auxiliary block cipher primitives.
        
        Stream Cipher State Initialization:
        Given a 256-bit Key (<i>K</i>) and a 128-bit Nonce (<i>N</i>):
        1. The state <b>S</b> is initialized with <b>IV</b>.
        2. The 32 bytes of <i>K</i> are absorbed into rate words <i>s<sub>0</sub> ... s<sub>3</sub></i>.
        3. The 16 bytes of <i>N</i> are absorbed into rate words <i>s<sub>4</sub> ... s<sub>5</sub></i>.
        4. Capacity word <i>s<sub>9</sub></i> is updated with the stream cipher domain:
           <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>S</b>[9] &larr; <b>S</b>[9] &oplus; <b>D</b><sub>cipher</sub>, <b>D</b><sub>cipher</sub> = 0x4843414349504852</font><br/>
        5. The state is mixed: <i><b>S</b> &larr; <b>M</b>(<b>S</b>)</i>.
        
        Keystream Generation & XOR Masking:
        For each 64-byte block of plaintext <i>P<sub>j</sub></i>:
        - A 64-byte keystream block <b>K</b><sub>j</sub> is extracted from rate words <i>s<sub>0</sub> ... s<sub>7</sub></i>.
        - Ciphertext is produced by bitwise XOR: <i>C<sub>j</sub> = P<sub>j</sub> &oplus; <b>K</b><sub>j</sub></i>.
        - Capacity word <i>s<sub>8</sub></i> absorbs block counter <i>j</i>: <i><b>S</b>[8] &larr; <b>S</b>[8] &oplus; j</i>.
        - The state is mixed for the next block: <i><b>S</b> &larr; <b>M</b>(<b>S</b>)</i>.
        """,
        """
        Security Considerations for Stream Mode:
        - Nonce Uniqueness: As with all stream ciphers (e.g., ChaCha20, AES-CTR), a (Key, Nonce) pair must never be reused. Nonce reuse immediately allows an attacker to compute C<sub>1</sub> &oplus; C<sub>2</sub> = P<sub>1</sub> &oplus; P<sub>2</sub>, compromising plaintext confidentiality.
        - Authentication Requirement: Unauthenticated stream ciphers are vulnerable to bit-flipping malleability attacks. Therefore, production usage requires the AEAD construction detailed in Section 19.
        """
    ),
    # PAGE 21
    (
        "19. Authenticated Encryption with Associated Data (AEAD)",
        "Duplex Sponge Authentication and Tag Verification",
        """
        To provide both confidentiality and ciphertext integrity simultaneously, HCA specifies a formal Authenticated Encryption with Associated Data (AEAD) mode following the duplex sponge paradigm.
        
        AEAD Encryption Protocol:
        1. Initialization:
           - Absorb 256-bit Key and 128-bit Nonce into state <b>S</b>.
           - Inject AEAD domain tag: <i><b>S</b>[9] &larr; <b>S</b>[9] &oplus; <b>D</b><sub>aead</sub></i> (<code>0x4843414145414400</code>).
           - Mix state: <i><b>S</b> &larr; <b>M</b>(<b>S</b>)</i>.
        2. Associated Data (<i>AD</i>) Processing:
           - Associated Data (e.g., packet headers, metadata) is absorbed into rate words <i>s<sub>0</sub> ... s<sub>7</sub></i>.
           - The state is mixed after each 64-byte block. No ciphertext is emitted during AD absorption.
        3. Plaintext Encryption & Ciphertext Absorption:
           - For each 64-byte plaintext block <i>P<sub>j</sub></i>, squeeze keystream <b>K</b><sub>j</sub> and compute <i>C<sub>j</sub> = P<sub>j</sub> &oplus; <b>K</b><sub>j</sub></i>.
           - Crucially, the ciphertext block <i>C<sub>j</sub></i> is immediately absorbed back into rate words <i>s<sub>0</sub> ... s<sub>7</sub></i> before the next state permutation:
             <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;<b>S</b>[0..7] &larr; <b>S</b>[0..7] &oplus; C<sub>j</sub>, <b>S</b> &larr; <b>M</b>(<b>S</b>)</font><br/>
             This binds the evolving ciphertext sequence irreversibly into the internal state.
        4. Authentication Tag Generation:
           - Squeeze 256 bits (32 bytes) from rate words <i>s<sub>0</sub> ... s<sub>3</sub></i> as the authentication tag <b>T</b>.
           - Emit payload: <code>Nonce || Tag || Ciphertext</code>.
        """,
        """
        AEAD Decryption & Constant-Time Verification:
        During decryption, the receiver re-absorbs Nonce, Key, and Associated Data, decrypts ciphertext, and re-computes tag <b>T'</b>. 
        The received tag <b>T</b> and calculated tag <b>T'</b> are compared in strict constant time. 
        If verification fails, the decrypted plaintext is wiped immediately and an error is raised, preventing chosen-ciphertext and padding-oracle attacks.
        """
    ),
    # PAGE 22
    (
        "20. Password Hashing & Key Derivation (hca_salted)",
        "Salt Formatting, Work Factors, and Brute-Force Economics",
        """
        While raw hash functions are optimized for high throughput, password storage requires deliberately sluggish or compute-hard constructions to resist mass GPU-accelerated dictionary cracking.
        
        To support basic password hashing requirements within experimental setups, HCA provides <code>hca_salted()</code>:
        <br/><font name="Courier-Bold" size="8.5" color="#0F172A">&nbsp;&nbsp;&nbsp;&nbsp;hca_salted(password, salt=None, output_bits=512) &rarr; "&lt;salt_hex&gt;:&lt;hash_hex&gt;"</font><br/>
        
        Salt Mechanics:
        1. A 16-byte (128-bit) cryptographically secure pseudorandom salt is generated via <code>os.urandom(16)</code>.
        2. The salt is prepended to the password bytes: <i>M = \text{Salt} || \text{Password}</i>.
        3. The message is digested via HCA-512.
        4. Output is formatted as a colon-delimited hex string.
        
        Verification Protocol:
        In <code>hca_verify_salted(password, stored_hash)</code>, the salt is extracted, prepended to the trial password, re-hashed, and compared against the stored hash in strict constant time using <code>hmac.compare_digest</code> to prevent timing attacks.
        """,
        """
        Production Guidance Warning:
        While hca_salted() provides basic salting against rainbow table attacks, high-speed ARX sponges are NOT memory-hard. 
        For production password storage, Hashium mandates the use of Argon2id (hashium_argon2) or scrypt, which consume megabytes of RAM to neutralize GPU/ASIC cracking arrays. HCA must never be used for production credentials.
        """
    )
]
