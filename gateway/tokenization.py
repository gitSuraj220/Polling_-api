"""Tokenization engine with Redis-backed session storage.

Tokenization replaces a sensitive value (e.g. a PAN — primary account number)
with an opaque, random token. The mapping ``token -> encrypted value`` lives in
Redis with a TTL. The stored value is itself encrypted at rest with the
AES-256-GCM utility, so a Redis dump alone never exposes plaintext.

Why this shape?
---------------
* **Random token, not a transform of the value.** The token carries no
  information about the PAN, so it is safe to log, store in your own DB, and
  pass around. Detokenization requires both Redis access *and* the encryption
  key.
* **Encryption at rest.** Even with the token, an attacker who reads Redis sees
  only AES-GCM ciphertext. The key is held by the application / a KMS, not in
  Redis.
* **AAD binding.** Each record is encrypted with the token as AAD, so a
  ciphertext copied under a different token key fails to decrypt.
* **TTL.** Tokens expire; sessions are not kept forever.

This module depends only on the ``redis`` client *interface*, so it works with a
real Redis server or an in-memory fake (``fakeredis``) in tests.
"""

from __future__ import annotations

import os
import secrets
import sys
from typing import Optional

# aes_gcm lives in the sibling crypto-utils/ directory (a hyphenated folder that
# is not an importable package), so we add it to sys.path. In a real project the
# crypto utility would be a proper installed module and this shim would go away.
try:  # pragma: no cover - import wiring
    from aes_gcm import AESGCMCipher, DecryptionError  # type: ignore
except ImportError:  # pragma: no cover
    sys.path.insert(
        0, os.path.join(os.path.dirname(__file__), "..", "crypto-utils")
    )
    from aes_gcm import AESGCMCipher, DecryptionError  # type: ignore

__all__ = ["TokenizationService", "TokenError"]

DEFAULT_TTL_SECONDS = 15 * 60  # 15 minutes
TOKEN_PREFIX = "tok_"
_REDIS_KEY_PREFIX = "tokenization:"


class TokenError(Exception):
    """Raised when a token cannot be detokenized (missing, expired, tampered)."""


class TokenizationService:
    """Tokenize / detokenize sensitive values with encryption + TTL.

    Parameters
    ----------
    redis_client:
        Any object implementing the subset of the redis API used here:
        ``set(name, value, ex=..., nx=...)``, ``get(name)``, ``delete(name)``,
        ``exists(name)``, ``ttl(name)``. Both ``redis.Redis`` and
        ``fakeredis.FakeRedis`` satisfy this.
    cipher:
        An :class:`AESGCMCipher` used to encrypt stored values at rest.
    default_ttl:
        Default token lifetime in seconds.
    """

    def __init__(
        self,
        redis_client,
        cipher: AESGCMCipher,
        default_ttl: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        if default_ttl <= 0:
            raise ValueError("default_ttl must be positive")
        self._redis = redis_client
        self._cipher = cipher
        self._default_ttl = default_ttl

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _new_token() -> str:
        return TOKEN_PREFIX + secrets.token_urlsafe(24)

    @staticmethod
    def _redis_key(token: str) -> str:
        return _REDIS_KEY_PREFIX + token

    # -- public API -------------------------------------------------------

    def tokenize(self, value: str, ttl: Optional[int] = None) -> str:
        """Store ``value`` encrypted and return a fresh opaque token.

        The token is bound to the ciphertext as AAD, so it cannot be reused
        with a different record.
        """
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        if value == "":
            raise ValueError("cannot tokenize an empty value")

        ttl = self._default_ttl if ttl is None else ttl
        if ttl <= 0:
            raise ValueError("ttl must be positive")

        # Generate a unique token (retry on the astronomically unlikely clash).
        for _ in range(5):
            token = self._new_token()
            key = self._redis_key(token)
            ciphertext = self._cipher.encrypt(
                value.encode("utf-8"), aad=token.encode("ascii")
            )
            # nx=True ensures we never overwrite an existing token.
            if self._redis.set(key, ciphertext, ex=ttl, nx=True):
                return token
        raise TokenError("could not allocate a unique token")  # pragma: no cover

    def detokenize(self, token: str) -> str:
        """Return the original value for ``token`` or raise :class:`TokenError`."""
        if not isinstance(token, str) or not token.startswith(TOKEN_PREFIX):
            raise TokenError("malformed token")

        raw = self._redis.get(self._redis_key(token))
        if raw is None:
            raise TokenError("token not found or expired")

        try:
            plaintext = self._cipher.decrypt(raw, aad=token.encode("ascii"))
        except DecryptionError as exc:
            # Stored ciphertext failed authentication -> treat as tampering.
            raise TokenError("stored value failed integrity check") from exc
        return plaintext.decode("utf-8")

    def revoke(self, token: str) -> bool:
        """Delete a token. Returns True if it existed."""
        if not isinstance(token, str):
            raise TokenError("malformed token")
        return bool(self._redis.delete(self._redis_key(token)))

    def exists(self, token: str) -> bool:
        return bool(self._redis.exists(self._redis_key(token)))

    def ttl(self, token: str) -> int:
        """Remaining TTL in seconds (-2 if missing, -1 if no expiry set)."""
        return int(self._redis.ttl(self._redis_key(token)))
