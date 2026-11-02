/// 1024-bit state represented as 16 unsigned 64-bit words.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct HCAState {
    pub s: [u64; 16],
}

impl HCAState {
    pub fn new(iv: &[u64; 16]) -> Self {
        Self { s: *iv }
    }
}
