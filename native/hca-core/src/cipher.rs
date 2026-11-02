use crate::hasher::HCAEngine;

/// Symmetric stream cipher encryption/decryption: ciphertext = plaintext ^ keystream.
pub fn cipher_process(data: &[u8], key: &[u8], nonce: &[u8]) -> Result<Vec<u8>, String> {
    let mut engine = HCAEngine::new(512)?;
    // Domain separation prefix for cipher mode
    engine.update(b"HCACIPHER:")?;
    engine.update(key)?;
    engine.update(b":")?;
    engine.update(nonce)?;

    let keystream = engine.squeeze_bytes(data.len());
    let processed = data
        .iter()
        .zip(keystream.iter())
        .map(|(&d, &k)| d ^ k)
        .collect();
    Ok(processed)
}
