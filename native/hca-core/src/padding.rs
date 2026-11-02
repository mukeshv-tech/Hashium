pub fn pad_message(message: &[u8]) -> Result<Vec<u8>, &'static str> {
    let len_bytes = message.len();
    let len_bits = (len_bytes as u128) * 8;
    if len_bits > u64::MAX as u128 {
        return Err("Message length exceeds maximum 64-bit capacity");
    }

    let rem = (len_bytes + 1) % 64;
    let k = (56 + 64 - rem) % 64;

    let total_len = len_bytes + 1 + k + 8;
    let mut padded = Vec::with_capacity(total_len);
    padded.extend_from_slice(message);
    padded.push(0x01);
    padded.resize(padded.len() + k, 0x00);
    padded.extend_from_slice(&(len_bits as u64).to_be_bytes());

    Ok(padded)
}
