use crate::constants::OUTPUT_DOMAIN;
use crate::permutation::mix_12_rounds;
use crate::state::HCAState;

pub fn squeeze(
    mut state: HCAState,
    output_bytes: usize,
    rc: &[[u64; 16]; 12],
) -> Vec<u8> {
    let mut output = Vec::with_capacity(output_bytes + 64);
    let mut q: u64 = 0;

    while output.len() < output_bytes {
        state.s[14] ^= OUTPUT_DOMAIN;
        state.s[15] ^= q;

        mix_12_rounds(&mut state, rc);

        for i in 0..8 {
            output.extend_from_slice(&state.s[i].to_be_bytes());
        }

        q = q.wrapping_add(1);
    }

    output.truncate(output_bytes);
    output
}
