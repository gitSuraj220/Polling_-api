"""Production-grade AES-256-GCM authenticated encryption utility.

Design notes
------------
* AES-256-GCM provides confidentiality *and* integrity. Any tampering with the
  ciphertext, nonce, or associated data causes decryption to fail loudly
  (``InvalidToken``) rather than returning corrupt plaintext.
* A fresh 96-bit (12-byte) nonce is generated from a CSPRNG (``os.urandom``)
  for **every** encryption. 96 bits is the size recommended by NIST SP 800-38D
  for GCM and lets the underlying library use the nonce directly without
  rehashing. Reusing a (key, nonce) pair with GCM is catastrophic — it breaks
  both confidentiality and integrity — so this class never lets the caller
  supply the nonce on encryption.
* Associated Authenticated Data (AAD) is authenticated but not encrypted. Use
  it to bind a ciphertext to its context (e.g. a record ID, user ID, or
  message version) so a ciphertext cannot be silently replayed in a different
  context. The same AAD must be supplied at decryption time.
* Wire format: ``nonce (12 bytes) || ciphertext+tag``. The 16-byte GCM tag is
  appended to the ciphertext by the underlying primitive. ``encrypt``/``decrypt``
  work on raw ``bytes``; ``encrypt_to_str``/``decrypt_from_str`` wrap that in
  URL-safe base64 for easy storage and transport.

Key handling best practices
---------------------------
* Keys are exactly 32 bytes (256 bits). The constructor validates this.
* ``generate_key`` returns a fresh CSPRNG key; ``generate_key_b64`` returns it
  base64-encoded for storage in a secrets manager / environment variable.
* In real systems, load the key from a dedicated secrets manager (AWS KMS,
  GCP KMS, HashiCorp Vault, etc.) — never hard-code it or commit it to source
  control. Rotate keys periodically and support decrypting with previous keys
  during a rotation window.
* ``__repr__`` and ``__str__`` never expose key material, reducing the risk of
  leaking the key into logs or tracebacks. Note: CPython cannot guarantee
  secure zeroing of immutable ``bytes`` in memory, so this class does not claim
  to scrub keys from RAM.
"""

from __future__ import annotations

import base64
import os
from typing import Optional

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

__all__ = ["AESGCMCipher", "DecryptionError"]

KEY_SIZE = 32   # AES-256 -> 256-bit key
NONCE_SIZE = 12  # 96-bit nonce recommended for GCM (NIST SP 800-38D)
TAG_SIZE = 16   # 128-bit GCM authentication tag (appended to ciphertext)


class DecryptionError(Exception):
    """Raised when decryption or authentication fails.

    This deliberately does not distinguish between a wrong key, a tampered
    ciphertext, mismatched AAD, or a malformed input, so callers cannot use the
    error to mount an oracle attack.
    """


class AESGCMCipher:
    """An AES-256-GCM cipher with random nonces and AAD support.

    Parameters
    ----------
    key:
        A 32-byte key. Use :meth:`generate_key` to create one, or load one from
        a secrets manager. Passing anything other than 32 ``bytes`` raises
        ``ValueError`` / ``TypeError``.
    """

    __slots__ = ("_aesgcm",)

    def __init__(self, key: bytes) -> None:
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError(f"key must be bytes, got {type(key).__name__}")
        if len(key) != KEY_SIZE:
            raise ValueError(
                f"key must be exactly {KEY_SIZE} bytes for AES-256, got {len(key)}"
            )
        # AESGCM copies the key into its own state.
        self._aesgcm = AESGCM(bytes(key))

    # -- key management ---------------------------------------------------

    @staticmethod
    def generate_key() -> bytes:
        """Return a fresh cryptographically random 32-byte key."""
        return AESGCM.generate_key(bit_length=256)

    @classmethod
    def generate_key_b64(cls) -> str:
        """Return a fresh key, base64-encoded for storage/transport."""
        return base64.urlsafe_b64encode(cls.generate_key()).decode("ascii")

    @classmethod
    def from_base64_key(cls, key_b64: str) -> "AESGCMCipher":
        """Build a cipher from a (url-safe) base64-encoded 32-byte key."""
        try:
            key = base64.urlsafe_b64decode(key_b64)
        except (ValueError, TypeError) as exc:
            raise ValueError("key_b64 is not valid base64") from exc
        return cls(key)

    # -- core API (bytes in, bytes out) -----------------------------------

    def encrypt(self, plaintext: bytes, aad: Optional[bytes] = None) -> bytes:
        """Encrypt ``plaintext`` and return ``nonce || ciphertext+tag``.

        A fresh random nonce is generated for every call. ``aad`` (if given) is
        authenticated but not encrypted and must be supplied again to decrypt.
        """
        if not isinstance(plaintext, (bytes, bytearray)):
            raise TypeError("plaintext must be bytes")
        if aad is not None and not isinstance(aad, (bytes, bytearray)):
            raise TypeError("aad must be bytes or None")

        nonce = os.urandom(NONCE_SIZE)
        ciphertext = self._aesgcm.encrypt(nonce, bytes(plaintext), _aad(aad))
        return nonce + ciphertext

    def decrypt(self, token: bytes, aad: Optional[bytes] = None) -> bytes:
        """Decrypt a ``nonce || ciphertext+tag`` token produced by :meth:`encrypt`.

        Raises :class:`DecryptionError` if authentication fails for any reason
        (wrong key, tampered data, mismatched AAD, truncated input).
        """
        if not isinstance(token, (bytes, bytearray)):
            raise TypeError("token must be bytes")
        if aad is not None and not isinstance(aad, (bytes, bytearray)):
            raise TypeError("aad must be bytes or None")
        # A valid token is at least nonce + tag; reject anything shorter before
        # touching the cipher.
        if len(token) < NONCE_SIZE + TAG_SIZE:
            raise DecryptionError("token is too short to be valid")

        nonce, ciphertext = token[:NONCE_SIZE], token[NONCE_SIZE:]
        try:
            return self._aesgcm.decrypt(nonce, bytes(ciphertext), _aad(aad))
        except InvalidTag as exc:
            raise DecryptionError("decryption failed: authentication error") from exc

    # -- convenience string API (base64) ----------------------------------

    def encrypt_to_str(self, plaintext: bytes, aad: Optional[bytes] = None) -> str:
        """Encrypt and return a URL-safe base64 string."""
        return base64.urlsafe_b64encode(self.encrypt(plaintext, aad)).decode("ascii")

    def decrypt_from_str(self, token_b64: str, aad: Optional[bytes] = None) -> bytes:
        """Decrypt a URL-safe base64 string produced by :meth:`encrypt_to_str`."""
        try:
            token = base64.urlsafe_b64decode(token_b64)
        except (ValueError, TypeError) as exc:
            raise DecryptionError("token is not valid base64") from exc
        return self.decrypt(token, aad)

    # -- safety: never leak key material in logs/tracebacks ---------------

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "AESGCMCipher(key=<hidden>)"

    __str__ = __repr__


def _aad(aad: Optional[bytes]) -> Optional[bytes]:
    """Normalise AAD: an empty ``b""`` and ``None`` must behave identically so
    callers don't get surprising auth failures from a falsy-but-present AAD."""
    if aad is None or len(aad) == 0:
        return None
    return bytes(aad)
