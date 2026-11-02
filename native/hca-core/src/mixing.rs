use crate::state::HCAState;

#[inline(always)]
pub fn rotl64(x: u64, shift: u32) -> u64 {
    x.rotate_left(shift % 64)
}

/// 12-round experimental mixing transformation.
pub fn mix_12_rounds(state: &mut HCAState, rc: &[[u64; 16]; 12]) {
    for r in 0..12 {
        let mut a = [0u64; 16];
        let mut b = [0u64; 16];
        let mut t = [0u64; 16];
        let mut s_new = [0u64; 16];

        let s = &state.s;

        for i in 0..16 {
            let s_next = s[(i + 1) % 16];
            let rot_val = rotl64(s_next ^ rc[r][i], 13);
            a[i] = s[i].wrapping_add(rot_val);

            let s_sum = s[(i + 4) % 16].wrapping_add(s[(i + 11) % 16]);
            b[i] = rotl64(s_sum, ((7 * i + 3 * r) % 64) as u32);

            t[i] = rotl64(a[i] ^ b[i], ((11 * i + 7 * r + 1) % 64) as u32);
        }

        for i in 0..16 {
            s_new[i] = t[(5 * i + r) % 16];
        }

        state.s = s_new;
    }
}
