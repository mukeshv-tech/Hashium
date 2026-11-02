pub mod absorb;
pub mod aead;
pub mod cipher;
pub mod constants;
pub mod hasher;
pub mod mixing;
pub mod output;
pub mod padding;
pub mod state;
pub mod tree;

use hasher::HCAEngine;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString, PyTuple};

#[pyclass(name = "HCAHasher", unsendable)]
pub struct PyHCAHasher {
    engine: HCAEngine,
}

#[pymethods]
impl PyHCAHasher {
    #[new]
    #[pyo3(signature = (output_bits=512))]
    pub fn new(output_bits: usize) -> PyResult<Self> {
        let engine = HCAEngine::new(output_bits).map_err(PyValueError::new_err)?;
        Ok(Self { engine })
    }

    pub fn update(&mut self, data: &Bound<'_, PyAny>) -> PyResult<()> {
        if data.is_instance_of::<PyString>() {
            return Err(PyTypeError::new_err(
                "Strings must be encoded to bytes before hashing",
            ));
        }

        let bytes_vec = if let Ok(py_bytes) = data.extract::<Vec<u8>>() {
            py_bytes
        } else {
            return Err(PyTypeError::new_err(
                "Expected bytes-like object (bytes, bytearray, or memoryview)",
            ));
        };

        self.engine
            .update(&bytes_vec)
            .map_err(PyValueError::new_err)?;
        Ok(())
    }

    pub fn digest<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        let output = self.engine.finalize();
        PyBytes::new(py, &output)
    }

    pub fn hexdigest(&self) -> String {
        let output = self.engine.finalize();
        let mut hex = String::with_capacity(output.len() * 2);
        for b in output {
            use std::fmt::Write;
            write!(&mut hex, "{:02x}", b).unwrap();
        }
        hex
    }

    pub fn copy(&self) -> Self {
        Self {
            engine: self.engine.clone(),
        }
    }

    pub fn reset(&mut self) {
        self.engine.reset();
    }

    #[getter]
    pub fn output_bits(&self) -> usize {
        self.engine.output_bits()
    }
}

#[pyfunction]
#[pyo3(signature = (data, output_bits=512))]
pub fn hca<'py>(
    py: Python<'py>,
    data: &Bound<'_, PyAny>,
    output_bits: usize,
) -> PyResult<Bound<'py, PyBytes>> {
    let mut hasher = PyHCAHasher::new(output_bits)?;
    hasher.update(data)?;
    Ok(hasher.digest(py))
}

#[pyfunction]
#[pyo3(signature = (data, output_bits=512))]
pub fn hca_parallel<'py>(
    py: Python<'py>,
    data: &[u8],
    output_bits: usize,
) -> PyResult<Bound<'py, PyBytes>> {
    let result = py.allow_threads(|| tree::tree_hash(data, output_bits))
        .map_err(PyValueError::new_err)?;
    Ok(PyBytes::new(py, &result))
}

#[pyfunction]
pub fn hca_cipher_process<'py>(
    py: Python<'py>,
    data: &[u8],
    key: &[u8],
    nonce: &[u8],
) -> PyResult<Bound<'py, PyBytes>> {
    let result = aead::cipher_process(data, key, nonce).map_err(PyValueError::new_err)?;
    Ok(PyBytes::new(py, &result))
}

#[pyfunction]
#[pyo3(signature = (plaintext, key, nonce, associated_data=None))]
pub fn hca_aead_encrypt<'py>(
    py: Python<'py>,
    plaintext: &[u8],
    key: &[u8],
    nonce: &[u8],
    associated_data: Option<&[u8]>,
) -> PyResult<Bound<'py, PyTuple>> {
    let ad = associated_data.unwrap_or(b"");
    let (ciphertext, tag) =
        aead::aead_encrypt(plaintext, key, nonce, ad).map_err(PyValueError::new_err)?;
    let py_cipher = PyBytes::new(py, &ciphertext);
    let py_tag = PyBytes::new(py, &tag);
    PyTuple::new(py, [py_cipher.as_any(), py_tag.as_any()])
}

#[pyfunction]
#[pyo3(signature = (ciphertext, key, nonce, tag, associated_data=None))]
pub fn hca_aead_decrypt<'py>(
    py: Python<'py>,
    ciphertext: &[u8],
    key: &[u8],
    nonce: &[u8],
    tag: &[u8],
    associated_data: Option<&[u8]>,
) -> PyResult<Bound<'py, PyBytes>> {
    let ad = associated_data.unwrap_or(b"");
    let plaintext = aead::aead_decrypt(ciphertext, key, nonce, ad, tag)
        .map_err(PyValueError::new_err)?;
    Ok(PyBytes::new(py, &plaintext))
}

#[pymodule]
fn _hca_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyHCAHasher>()?;
    m.add_function(wrap_pyfunction!(hca, m)?)?;
    m.add_function(wrap_pyfunction!(hca_parallel, m)?)?;
    m.add_function(wrap_pyfunction!(hca_cipher_process, m)?)?;
    m.add_function(wrap_pyfunction!(hca_aead_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(hca_aead_decrypt, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_engine_basic() {
        let mut engine = HCAEngine::new(512).unwrap();
        engine.update(b"Hello Hashium").unwrap();
        let d = engine.finalize();
        assert_eq!(d.len(), 64);
    }

    #[test]
    fn test_aead_roundtrip() {
        let key = b"mysecretpasswordkey123";
        let nonce = b"1234567812345678";
        let ad = b"header-metadata";
        let plaintext = b"Hello AEAD Authenticated World!";

        let (cipher, tag) = aead::aead_encrypt(plaintext, key, nonce, ad).unwrap();
        let decrypted = aead::aead_decrypt(&cipher, key, nonce, ad, &tag).unwrap();
        assert_eq!(plaintext.to_vec(), decrypted);

        // Tamper test
        let mut tampered_cipher = cipher.clone();
        tampered_cipher[0] ^= 0x01;
        assert!(aead::aead_decrypt(&tampered_cipher, key, nonce, ad, &tag).is_err());
    }

    #[test]
    fn test_tree_parallel() {
        let data = vec![0x42u8; 100 * 1024];
        let hash = tree::tree_hash(&data, 256).unwrap();
        assert_eq!(hash.len(), 32);
    }
}
