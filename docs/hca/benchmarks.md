# HCA Benchmark Methodology & Results

## 1. Methodology
Benchmarks measure the performance and throughput of the native **HCA-0.2** Rust prototype compared to standard implementations in Python (`hashlib` for SHA-256 and SHA3-256, and BLAKE3 where available).

- **Environment**: Windows x86_64, Python 3.14, Rust 1.99.1.
- **Sizes tested**:
  - Small: 64 Bytes (1 absorption block)
  - Medium: 1 Kilobyte
  - Large: 1 Megabyte
  - Extra Large: 10 Megabytes
- **Iterations**: High repetition on small sizes to amortize timing overhead; repeated trials for large files.
- **Metrics**: Total elapsed wall-clock time and calculated throughput in Megabytes per second (MB/s).

## 2. Benchmark Results

| Input Size | Algorithm | Total Time (s) | Throughput (MB/s) |
|---|---|---|---|
| **64 B** | **HCA-0.2 (256b)** | 0.0179 s | **34.06 MB/s** |
| 64 B | **HCA-0.2 (512b)** | 0.0176 s | **34.71 MB/s** |
| 64 B | SHA-256 (C/OpenSSL) | 0.0039 s | 156.77 MB/s |
| 64 B | SHA3-256 (C) | 0.0061 s | 100.26 MB/s |
| **1 KB** | **HCA-0.2 (256b)** | 0.0732 s | **66.72 MB/s** |
| 1 KB | **HCA-0.2 (512b)** | 0.0806 s | **60.59 MB/s** |
| 1 KB | SHA-256 (C/OpenSSL) | 0.0041 s | 1202.90 MB/s |
| 1 KB | SHA3-256 (C) | 0.0103 s | 472.47 MB/s |
| **1 MB** | **HCA-0.2 (256b)** | 0.3106 s | **64.39 MB/s** |
| 1 MB | **HCA-0.2 (512b)** | 0.3281 s | **60.96 MB/s** |
| 1 MB | SHA-256 (C/OpenSSL) | 0.0149 s | 1338.27 MB/s |
| 1 MB | SHA3-256 (C) | 0.0357 s | 560.13 MB/s |
| **10 MB** | **HCA-0.2 (256b)** | 0.4443 s | **67.52 MB/s** |
| 10 MB | **HCA-0.2 (512b)** | 0.4877 s | **61.51 MB/s** |
| 10 MB | SHA-256 (C/OpenSSL) | 0.0143 s | 2096.01 MB/s |
| 10 MB | SHA3-256 (C) | 0.0528 s | 567.75 MB/s |

## 3. Observations & Analysis
- **HCA-0.2 Sustained Throughput**: Achieves ~60–68 MB/s on large streams with safe Rust scalar execution.
- **Hardware Acceleration Comparison**: Standard SHA-256 achieves >1.3–2.0 GB/s due to Intel SHA-NI / AVX2 hardware assembly instructions in OpenSSL.
- **Security Clarification**: Performance speed does **NOT** indicate cryptographic security, collision resistance, or preimage resistance. HCA-0.2 remains strictly an experimental research construction.
