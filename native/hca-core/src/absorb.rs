use crate::constants::ABSORB_DOMAIN;
use crate::permutation::mix_12_rounds;
use crate::state::HCAState;

pub fn absorb_block(
    state: &mut HCAState,
    block: &[u8; 64],
    block_index: u64,
    rc: &[[u64; 16]; 12],
) {
    for i in 0..8 {
        let chunk: [u8; 8] = block[i * 8..(i + 1) * 8].try_into().unwrap();
        let word = u64::from_be_bytes(chunk);
        state.s[i] ^= word;
    }

    state.s[8] ^= block_index;
    state.s[9] ^= ABSORB_DOMAIN;

    mix_12_rounds(state, rc);
}
