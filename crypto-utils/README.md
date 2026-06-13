# AES-256-GCM Encryption Utility

A small, production-grade authenticated-encryption helper built on the
[`cryptography`](https://cryptography.io) library.

## Features

- **AES-256-GCM** — confidentiality **and** integrity in one primitive.
- **Random 96-bit nonce per message** (NIST SP 800-38D), generated from a
  CSPRNG. The caller can never supply the nonce on encryption, so the
  catastrophic (key, nonce) reuse failure mode is impossible by construction.
- **AAD support** — bind a ciphertext to its context (record id, user id, …);
  tampering with the AAD makes decryption fail.
- **Tamper detection** — any change to the nonce, ciphertext, tag, or AAD
  raises `DecryptionError`.
- **Safe key handling** — strict 32-byte key validation, base64 helpers, and a
  `__repr__` that never leaks key material into logs/tracebacks.

## Install

```bash
pip install cryptography pytest
```

## Usage

```python
from aes_gcm import AESGCMCipher

# Generate (and store securely in a secrets manager) a key:
key_b64 = AESGCMCipher.generate_key_b64()

cipher = AESGCMCipher.from_base64_key(key_b64)

# Encrypt, binding the ciphertext to a context via AAD:
token = cipher.encrypt_to_str(b"4111 1111 1111 1111", aad=b"user-42")

# Decrypt (the same AAD must be supplied):
plaintext = cipher.decrypt_from_str(token, aad=b"user-42")  # -> b"4111 ..."
```

## Run the tests

```bash
python -m pytest -q
```

## Production notes

- Load keys from a dedicated secrets manager (AWS KMS, GCP KMS, Vault) — never
  hard-code or commit them.
- Rotate keys periodically; keep previous keys available to decrypt old data
  during the rotation window.
- For payment-card data specifically, prefer reducing PCI-DSS scope by using a
  certified processor (Stripe, Adyen, Braintree) over storing PANs yourself.
- CPython cannot guarantee secure zeroing of immutable `bytes`, so this class
  does not claim to scrub key material from memory.
