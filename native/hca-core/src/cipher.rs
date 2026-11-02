use crate::hasher::HCAEngine;

/// Generate keystream using HCA state initialized from key and nonce.
pub fn generate_keystream(key: &[u8], nonce: &[u8], len: usize) -> Result<Vec<u8>, String> {
    let mut engine = HCAEngine::new(512)?;
    // Domain separation prefix for cipher mode
    engine.update(b"HCACIPHER:")?;
    engine.update(key)?;
    engine.update(b":")?;
    engine.update(nonce)?;

    let keystream = engine.squeeze_bytes(len);
    Ok(keystream)
}
