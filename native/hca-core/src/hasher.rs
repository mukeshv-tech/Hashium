use crate::absorb::absorb_block;
use crate::constants::generate_constants;
use crate::output::squeeze;
use crate::state::HCAState;

#[derive(Clone, Debug)]
pub struct HCAEngine {
    state: HCAState,
    buffer: Vec<u8>,
    total_length: u64,
    block_count: u64,
    output_bits: usize,
    output_bytes: usize,
    iv: [u64; 16],
    rc: [[u64; 16]; 12],
}

impl HCAEngine {
    pub fn new(output_bits: usize) -> Result<Self, String> {
        if !(128..=4096).contains(&output_bits) || !output_bits.is_multiple_of(8) {
            return Err(format!(
                "output_bits must be between 128 and 4096 and a multiple of 8, got {}",
                output_bits
            ));
        }

        let (iv, rc) = generate_constants();
        let state = HCAState::new(&iv);

        Ok(Self {
            state,
            buffer: Vec::with_capacity(64),
            total_length: 0,
            block_count: 0,
            output_bits,
            output_bytes: output_bits / 8,
            iv,
            rc,
        })
    }

    pub fn update(&mut self, data: &[u8]) -> Result<(), String> {
        let added_len = data.len() as u64;
        let (new_total, overflow) = self.total_length.overflowing_add(added_len);
        if overflow || (new_total as u128) * 8 > u64::MAX as u128 {
            return Err("Input message length exceeds 64-bit capacity".to_string());
        }
        self.total_length = new_total;

        let mut data_slice = data;
        if !self.buffer.is_empty() {
            let needed = 64 - self.buffer.len();
            if data_slice.len() >= needed {
                self.buffer.extend_from_slice(&data_slice[..needed]);
                data_slice = &data_slice[needed..];
                let mut block = [0u8; 64];
                block.copy_from_slice(&self.buffer);
                absorb_block(&mut self.state, &block, self.block_count, &self.rc);
                self.block_count = self.block_count.wrapping_add(1);
                self.buffer.clear();
            } else {
                self.buffer.extend_from_slice(data_slice);
                return Ok(());
            }
        }

        while data_slice.len() >= 64 {
            let block: &[u8; 64] = data_slice[..64].try_into().unwrap();
            absorb_block(&mut self.state, block, self.block_count, &self.rc);
            self.block_count = self.block_count.wrapping_add(1);
            data_slice = &data_slice[64..];
        }

        if !data_slice.is_empty() {
            self.buffer.extend_from_slice(data_slice);
        }

        Ok(())
    }

    pub fn reset(&mut self) {
        self.state = HCAState::new(&self.iv);
        self.buffer.clear();
        self.total_length = 0;
        self.block_count = 0;
    }

    pub fn finalize(&self) -> Vec<u8> {
        let mut state = self.state;
        let mut block_count = self.block_count;

        let rem = (self.buffer.len() + 1) % 64;
        let k = (56 + 64 - rem) % 64;
        let len_bits = self.total_length.wrapping_mul(8);

        let mut padded = Vec::with_capacity(self.buffer.len() + 1 + k + 8);
        padded.extend_from_slice(&self.buffer);
        padded.push(0x01);
        padded.resize(padded.len() + k, 0x00);
        padded.extend_from_slice(&len_bits.to_be_bytes());

        let (chunks, _) = padded.as_chunks::<64>();
        for block in chunks {
            absorb_block(&mut state, block, block_count, &self.rc);
            block_count = block_count.wrapping_add(1);
        }

        squeeze(state, self.output_bytes, &self.rc)
    }

    pub fn squeeze_bytes(&self, bytes: usize) -> Vec<u8> {
        let mut state = self.state;
        let mut block_count = self.block_count;

        let rem = (self.buffer.len() + 1) % 64;
        let k = (56 + 64 - rem) % 64;
        let len_bits = self.total_length.wrapping_mul(8);

        let mut padded = Vec::with_capacity(self.buffer.len() + 1 + k + 8);
        padded.extend_from_slice(&self.buffer);
        padded.push(0x01);
        padded.resize(padded.len() + k, 0x00);
        padded.extend_from_slice(&len_bits.to_be_bytes());

        let (chunks, _) = padded.as_chunks::<64>();
        for block in chunks {
            absorb_block(&mut state, block, block_count, &self.rc);
            block_count = block_count.wrapping_add(1);
        }

        squeeze(state, bytes, &self.rc)
    }

    pub fn output_bits(&self) -> usize {
        self.output_bits
    }
}
