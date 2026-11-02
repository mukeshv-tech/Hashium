use crate::hasher::HCAEngine;
use rayon::prelude::*;

const LEAF_CHUNK_SIZE: usize = 16 * 1024; // 16 KB chunks for optimal L1/L2 cache utilization
const TREE_DOMAIN: &[u8] = b"HCATREE:";

/// Compute high-throughput parallel tree hash of large byte slices using all CPU cores.
/// If payload is smaller than 2 chunks (32 KB), falls back to single-pass sequential HCA.
pub fn tree_hash(data: &[u8], output_bits: usize) -> Result<Vec<u8>, String> {
    if data.len() < LEAF_CHUNK_SIZE * 2 {
        let mut engine = HCAEngine::new(output_bits)?;
        engine.update(data)?;
        return Ok(engine.finalize());
    }

    // Split input into 16 KB chunks and hash in parallel using Rayon worker threads
    let chunks: Vec<&[u8]> = data.chunks(LEAF_CHUNK_SIZE).collect();
    let mut current_nodes: Vec<Vec<u8>> = chunks
        .into_par_iter()
        .enumerate()
        .map(|(idx, chunk)| {
            let mut leaf_engine = HCAEngine::new(512).unwrap();
            let mut prefix = [0u8; 16];
            prefix[..8].copy_from_slice(b"HCALEAF:");
            prefix[8..16].copy_from_slice(&(idx as u64).to_be_bytes());
            leaf_engine.update(&prefix).unwrap();
            leaf_engine.update(chunk).unwrap();
            leaf_engine.finalize()
        })
        .collect();

    // Reduce binary tree levels down to root
    while current_nodes.len() > 1 {
        let next_level: Vec<Vec<u8>> = current_nodes
            .par_chunks(2)
            .map(|pair| {
                let mut node_engine = HCAEngine::new(512).unwrap();
                node_engine.update(TREE_DOMAIN).unwrap();
                node_engine.update(&pair[0]).unwrap();
                if pair.len() > 1 {
                    node_engine.update(&pair[1]).unwrap();
                }
                node_engine.finalize()
            })
            .collect();
        current_nodes = next_level;
    }

    // Root squeeze with requested output bits
    let mut root_engine = HCAEngine::new(output_bits)?;
    root_engine.update(b"HCAROOT:").unwrap();
    root_engine.update(&current_nodes[0]).unwrap();
    root_engine.update(&(data.len() as u64).to_be_bytes()).unwrap();
    Ok(root_engine.finalize())
}
