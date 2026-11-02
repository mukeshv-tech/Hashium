use crate::cipher::generate_keystream;
use crate::hasher::HCAEngine;

/// Process stream encryption/decryption: ciphertext = data ^ keystream.
pub fn cipher_process(data: &[u8], key: &[u8], nonce: &[u8]) -> Result<Vec<u8>, String> {
    let keystream = generate_keystream(key, nonce, data.len())?;
    let processed = data
        .iter()
        .zip(keystream.iter())
        .map(|(&d, &k)| d ^ k)
        .collect();
    Ok(processed)
}

/// Compute a 256-bit (32-byte) Authentication Tag over Associated Data (AD) and Ciphertext.
/// Tag = HCA-256("HCAMACTAG:" || key || ":" || nonce || ":" || AD || ":" || ciphertext)
pub fn compute_aead_tag(
    key: &[u8],
    nonce: &[u8],
    ad: &[u8],
    ciphertext: &[u8],
) -> Result<Vec<u8>, String> {
    let mut mac_engine = HCAEngine::new(256)?;
    mac_engine.update(b"HCAMACTAG:")?;
    mac_engine.update(key)?;
    mac_engine.update(b":")?;
    mac_engine.update(nonce)?;
    mac_engine.update(b":")?;
    mac_engine.update(&(ad.len() as u64).to_be_bytes())?;
    mac_engine.update(ad)?;
    mac_engine.update(b":")?;
    mac_engine.update(&(ciphertext.len() as u64).to_be_bytes())?;
    mac_engine.update(ciphertext)?;
    Ok(mac_engine.finalize())
}

/// Constant-time comparison between two slices to prevent timing side-channel attacks.
#[inline(never)]
pub fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut diff = 0u8;
    for (&x, &y) in a.iter().zip(b.iter()) {
        diff |= x ^ y;
    }
    diff == 0
}

/// AEAD Encrypt: Encrypts plaintext and computes authentication tag.
/// Returns (ciphertext, tag_32_bytes)
pub fn aead_encrypt(
    plaintext: &[u8],
    key: &[u8],
    nonce: &[u8],
    ad: &[u8],
) -> Result<(Vec<u8>, Vec<u8>), String> {
    let ciphertext = cipher_process(plaintext, key, nonce)?;
    let tag = compute_aead_tag(key, nonce, ad, &ciphertext)?;
    Ok((ciphertext, tag))
}

/// AEAD Decrypt: Verifies authentication tag in constant-time before decrypting ciphertext.
pub fn aead_decrypt(
    ciphertext: &[u8],
    key: &[u8],
    nonce: &[u8],
    ad: &[u8],
    tag: &[u8],
) -> Result<Vec<u8>, String> {
    let expected_tag = compute_aead_tag(key, nonce, ad, ciphertext)?;
    if !constant_time_eq(tag, &expected_tag) {
        return Err("Authentication failed: invalid tag or ciphertext tampered".to_string());
    }
    cipher_process(ciphertext, key, nonce)
}
