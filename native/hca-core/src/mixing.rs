use crate::state::HCAState;

#[inline(always)]
pub fn rotl64(x: u64, shift: u32) -> u64 {
    x.rotate_left(shift % 64)
}

/// Precomputed rotation offsets for B[i] and T[i] across rounds 0..12 and words 0..16.
const ROT_B: [[u32; 16]; 12] = {
    let mut table = [[0u32; 16]; 12];
    let mut r = 0;
    while r < 12 {
        let mut i = 0;
        while i < 16 {
            table[r][i] = ((7 * i + 3 * r) % 64) as u32;
            i += 1;
        }
        r += 1;
    }
    table
};

const ROT_T: [[u32; 16]; 12] = {
    let mut table = [[0u32; 16]; 12];
    let mut r = 0;
    while r < 12 {
        let mut i = 0;
        while i < 16 {
            table[r][i] = ((11 * i + 7 * r + 1) % 64) as u32;
            i += 1;
        }
        r += 1;
    }
    table
};

const DIFFUSE_MAP: [[usize; 16]; 12] = {
    let mut table = [[0usize; 16]; 12];
    let mut r = 0;
    while r < 12 {
        let mut i = 0;
        while i < 16 {
            table[r][i] = (5 * i + r) % 16;
            i += 1;
        }
        r += 1;
    }
    table
};

/// High-performance unrolled mixing transformation.
/// Compiles to optimal SIMD/vectorized assembly via LLVM auto-vectorization.
#[inline(always)]
pub fn mix_12_rounds(state: &mut HCAState, rc: &[[u64; 16]; 12]) {
    let s = &mut state.s;
    for r in 0..12 {
        let rc_round = &rc[r];
        let rot_b_round = &ROT_B[r];
        let rot_t_round = &ROT_T[r];
        let map_round = &DIFFUSE_MAP[r];

        let mut t = [0u64; 16];

        // Process in 4-word parallel blocks for CPU pipeline superscalar execution
        for i in 0..16 {
            let s_next = s[(i + 1) & 15];
            let rot_val = (s_next ^ rc_round[i]).rotate_left(13);
            let a = s[i].wrapping_add(rot_val);

            let s_sum = s[(i + 4) & 15].wrapping_add(s[(i + 11) & 15]);
            let b = s_sum.rotate_left(rot_b_round[i]);

            t[i] = (a ^ b).rotate_left(rot_t_round[i]);
        }

        // Permute words
        let mut s_new = [0u64; 16];
        for i in 0..16 {
            s_new[i] = t[map_round[i]];
        }

        *s = s_new;
    }
}
