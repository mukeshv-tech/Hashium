use crate::constants::ABSORB_DOMAIN;
use crate::mixing::mix_12_rounds;
use crate::state::HCAState;

#[inline(always)]
pub fn absorb_block(
    state: &mut HCAState,
    block: &[u8; 64],
    block_index: u64,
    rc: &[[u64; 16]; 12],
) {
    // Unroll and decode 8 64-bit big-endian words without per-iteration slicing bounds checks
    let ptr = block.as_ptr() as *const [u8; 8];
    unsafe {
        state.s[0] ^= u64::from_be_bytes(*ptr.add(0));
        state.s[1] ^= u64::from_be_bytes(*ptr.add(1));
        state.s[2] ^= u64::from_be_bytes(*ptr.add(2));
        state.s[3] ^= u64::from_be_bytes(*ptr.add(3));
        state.s[4] ^= u64::from_be_bytes(*ptr.add(4));
        state.s[5] ^= u64::from_be_bytes(*ptr.add(5));
        state.s[6] ^= u64::from_be_bytes(*ptr.add(6));
        state.s[7] ^= u64::from_be_bytes(*ptr.add(7));
    }

    state.s[8] ^= block_index;
    state.s[9] ^= ABSORB_DOMAIN;

    mix_12_rounds(state, rc);
}
