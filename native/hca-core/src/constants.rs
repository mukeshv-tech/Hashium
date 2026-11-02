/// Initial seed: ASCII "HCA-v01\0"
pub const SPLITMIX64_SEED: u64 = 0x4843412D76303100;
pub const ABSORB_DOMAIN: u64 = 0x4843414142534F52;
pub const OUTPUT_DOMAIN: u64 = 0x4843414F55545055;

#[derive(Clone, Debug)]
pub struct SplitMix64 {
    x: u64,
}

impl SplitMix64 {
    pub fn new(seed: u64) -> Self {
        Self { x: seed }
    }

    #[inline]
    pub fn next_u64(&mut self) -> u64 {
        self.x = self.x.wrapping_add(0x9E3779B97F4A7C15);
        let mut z = self.x;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
        z ^ (z >> 31)
    }
}

pub const CONST_IV: [u64; 16] = {
    let mut sm = SplitMix64 { x: SPLITMIX64_SEED };
    let mut iv = [0u64; 16];
    let mut i = 0;
    while i < 16 {
        sm.x = sm.x.wrapping_add(0x9E3779B97F4A7C15);
        let mut z = sm.x;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
        iv[i] = z ^ (z >> 31);
        i += 1;
    }
    iv
};

pub const CONST_RC: [[u64; 16]; 12] = {
    let mut sm = SplitMix64 { x: SPLITMIX64_SEED };
    // Skip 16 for IV
    let mut i = 0;
    while i < 16 {
        sm.x = sm.x.wrapping_add(0x9E3779B97F4A7C15);
        i += 1;
    }
    let mut rc = [[0u64; 16]; 12];
    let mut r = 0;
    while r < 12 {
        let mut j = 0;
        while j < 16 {
            sm.x = sm.x.wrapping_add(0x9E3779B97F4A7C15);
            let mut z = sm.x;
            z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
            rc[r][j] = z ^ (z >> 31);
            j += 1;
        }
        r += 1;
    }
    rc
};

pub fn generate_constants() -> ([u64; 16], [[u64; 16]; 12]) {
    (CONST_IV, CONST_RC)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_splitmix64_deterministic() {
        let (iv, rc) = generate_constants();
        assert_eq!(iv.len(), 16);
        assert_eq!(rc.len(), 12);
        assert_ne!(iv[0], 0);
        assert_ne!(rc[0][0], 0);
    }
}
