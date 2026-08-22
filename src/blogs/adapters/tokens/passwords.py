"""Admin password hashing.

``hashlib.scrypt``, from the standard library. Two reasons over reaching for
argon2 or bcrypt:

* **Memory-hard.** A password is low-entropy and long-lived, so unlike the OTP
  codes and refresh secrets in ``codecs.py`` it genuinely can be brute-forced
  offline from a stolen database. scrypt's cost is memory as well as time,
  which is what blunts GPU and ASIC attacks — plain SHA-256 would not.
* **No dependency.** Password hashing is the last place to want an unaudited
  transitive dependency, and the stdlib implementation is OpenSSL's.

Argon2id would be the marginally stronger choice and is worth revisiting if a
dependency is ever acceptable; scrypt at these parameters is not the weak link.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

#: n=2^15, r=8, p=1 → 128 · r · n = 32 MiB per hash and roughly 100 ms on
#: ordinary hardware. Slow enough to make offline guessing expensive, fast
#: enough that one admin sign-in is imperceptible.
_N = 2**15
_R = 8
_P = 1
_DKLEN = 32
_SALT_BYTES = 16

#: OpenSSL caps scrypt memory at ~32 MiB unless told otherwise, and the
#: parameters above sit exactly at that edge. Stated explicitly with headroom so
#: this raises at no point in the future for a reason nobody expects.
_MAXMEM = 96 * 1024 * 1024

#: Stored layout: salt ‖ derived key. The migration CHECKs this length.
STORED_LENGTH = _SALT_BYTES + _DKLEN


def _derive(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_N,
        r=_R,
        p=_P,
        dklen=_DKLEN,
        maxmem=_MAXMEM,
    )


class ScryptPasswordHasher:
    def hash(self, password: str) -> bytes:
        """Hash with a fresh random salt.

        Per-password salt, not a global one: identical passwords must produce
        different stored values, or the database reveals which accounts share a
        password and one cracked hash breaks all of them.
        """
        salt = secrets.token_bytes(_SALT_BYTES)
        return salt + _derive(password, salt)

    def verify(self, password: str, stored: bytes | None) -> bool:
        """Check a password against a stored hash.

        Returns False rather than raising when ``stored`` is absent — but note
        it still performs a full derivation against a dummy salt first. Without
        that, "no password set" would return in microseconds while a real check
        takes ~100 ms, and the difference is a reliable oracle for which
        accounts exist and which have credentials.
        """
        if stored is None or len(stored) != STORED_LENGTH:
            _derive(password, b"\x00" * _SALT_BYTES)
            return False

        salt, expected = stored[:_SALT_BYTES], stored[_SALT_BYTES:]
        # Constant-time: a byte-wise == leaks the position of the first
        # mismatch through timing.
        return hmac.compare_digest(_derive(password, salt), expected)
