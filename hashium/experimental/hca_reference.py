"""
HCA-0.1 Independent Pure Python Reference Implementation.

This module is designed strictly according to the HCA-0.1 specification
for verification, testing, and test vector generation. It does NOT use
the native Rust extension.
"""

from typing import List, Union

MASK64 = 0xFFFFFFFFFFFFFFFF
SPLITMIX64_SEED = 0x4843412D76303100
ABSORB_DOMAIN = 0x4843414142534F52
OUTPUT_DOMAIN = 0x4843414F55545055


def rotl64(x: int, shift: int) -> int:
    shift = shift % 64
    x &= MASK64
    return ((x << shift) & MASK64) | (x >> (64 - shift)) if shift > 0 else x


class SplitMix64:
    def __init__(self, seed: int = SPLITMIX64_SEED):
        self.x = seed & MASK64

    def next_u64(self) -> int:
        self.x = (self.x + 0x9E3779B97F4A7C15) & MASK64
        z = self.x
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        z = (z ^ (z >> 31)) & MASK64
        return z


def generate_constants() -> tuple:
    """Generate (IV, RC) where IV is 16 u64s and RC is 12x16 u64s."""
    sm = SplitMix64(SPLITMIX64_SEED)
    iv = [sm.next_u64() for _ in range(16)]
    rc = [[sm.next_u64() for _ in range(16)] for _ in range(12)]
    return iv, rc


IV_CONSTANTS, RC_CONSTANTS = generate_constants()


def mix_12_rounds(state: List[int], rc_table: List[List[int]] = RC_CONSTANTS) -> List[int]:
    """Execute the 12-round experimental mixing function on a 16-word state."""
    s = list(state)
    for r in range(12):
        a = [0] * 16
        b = [0] * 16
        t = [0] * 16
        s_new = [0] * 16

        for i in range(16):
            a[i] = (s[i] + rotl64((s[(i + 1) % 16] ^ rc_table[r][i]) & MASK64, 13)) & MASK64
            b[i] = rotl64((s[(i + 4) % 16] + s[(i + 11) % 16]) & MASK64, (7 * i + 3 * r) % 64)
            t[i] = rotl64((a[i] ^ b[i]) & MASK64, (11 * i + 7 * r + 1) % 64)

        for i in range(16):
            s_new[i] = t[(5 * i + r) % 16]

        s = s_new
    return s


def pad_message(message: bytes) -> bytes:
    """Apply HCA-0.1 padding to input message bytes."""
    length_bytes = len(message)
    length_bits = length_bytes * 8
    if length_bits >= (1 << 64):
        raise ValueError("Message length exceeds maximum 64-bit capacity")

    # M || 0x01 || 0x00... || BE64(8 * len(M))
    # Find smallest k >= 0 such that (len(M) + 1 + k) % 64 == 56
    rem = (length_bytes + 1) % 64
    k = (56 - rem) % 64
    padding = b"\x01" + (b"\x00" * k) + length_bits.to_bytes(8, byteorder="big")
    return message + padding


class HCAReferenceHasher:
    def __init__(self, output_bits: int = 512):
        if not (128 <= output_bits <= 4096 and output_bits % 8 == 0):
            raise ValueError(
                f"output_bits must be between 128 and 4096 and a multiple of 8, got {output_bits}"
            )
        self.output_bits = output_bits
        self.output_bytes = output_bits // 8
        self.buffer = bytearray()
        self.total_length = 0
        self.state = list(IV_CONSTANTS)
        self.block_count = 0

    def update(self, data: Union[bytes, bytearray, memoryview]) -> "HCAReferenceHasher":
        if isinstance(data, str):
            raise TypeError("Strings must be encoded to bytes before hashing")
        data_bytes = bytes(data)
        self.total_length += len(data_bytes)
        self.buffer.extend(data_bytes)

        while len(self.buffer) >= 64:
            block = bytes(self.buffer[:64])
            del self.buffer[:64]
            self._absorb_block(block)

        return self

    def _absorb_block(self, block: bytes) -> None:
        m = [int.from_bytes(block[i * 8 : (i + 1) * 8], byteorder="big") for i in range(8)]
        for i in range(8):
            self.state[i] ^= m[i]
        self.state[8] ^= self.block_count
        self.state[9] ^= ABSORB_DOMAIN
        self.state = mix_12_rounds(self.state)
        self.block_count += 1

    def copy(self) -> "HCAReferenceHasher":
        new_hasher = HCAReferenceHasher(self.output_bits)
        new_hasher.buffer = bytearray(self.buffer)
        new_hasher.total_length = self.total_length
        new_hasher.state = list(self.state)
        new_hasher.block_count = self.block_count
        return new_hasher

    def reset(self) -> "HCAReferenceHasher":
        self.buffer = bytearray()
        self.total_length = 0
        self.state = list(IV_CONSTANTS)
        self.block_count = 0
        return self

    def digest(self) -> bytes:
        # Clone current state and process final padded blocks
        state = list(self.state)
        block_count = self.block_count

        # Pad remaining buffer
        length_bits = self.total_length * 8
        rem = (len(self.buffer) + 1) % 64
        k = (56 - rem) % 64
        padded = bytes(self.buffer) + b"\x01" + (b"\x00" * k) + length_bits.to_bytes(8, byteorder="big")

        for i in range(0, len(padded), 64):
            block = padded[i : i + 64]
            m = [int.from_bytes(block[j * 8 : (j + 1) * 8], byteorder="big") for j in range(8)]
            for j in range(8):
                state[j] ^= m[j]
            state[8] ^= block_count
            state[9] ^= ABSORB_DOMAIN
            state = mix_12_rounds(state)
            block_count += 1

        # Squeezing phase
        output = bytearray()
        q = 0
        while len(output) < self.output_bytes:
            state[14] ^= OUTPUT_DOMAIN
            state[15] ^= q
            state = mix_12_rounds(state)
            for j in range(8):
                output.extend(state[j].to_bytes(8, byteorder="big"))
            q += 1

        return bytes(output[: self.output_bytes])

    def hexdigest(self) -> str:
        return self.digest().hex()


def hca_reference(data: Union[bytes, bytearray, memoryview], output_bits: int = 512) -> bytes:
    hasher = HCAReferenceHasher(output_bits=output_bits)
    hasher.update(data)
    return hasher.digest()
