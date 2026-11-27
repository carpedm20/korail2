# -*- coding: utf-8 -*-
"""
    korail2.dynapath
    ~~~~~~~~~~~~~~~~

    Minimal generator for the ``x-dynapath-m-token`` header that Korail's
    macro guard requires on the login, schedule, fare and reservation
    endpoints.

    :copyright: (c) 2026 korail2 contributors.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import math
import secrets
import struct
import time

TOKEN_PREFIX = "201"

# Build-embedded secret of the DynaPath mobile SDK (public protocol constant,
# not a user credential). 64 ASCII hex characters used as raw ASCII bytes.
_SECRET = b"9a330fd663b62c5f888a7ce76ac7202d93f646b4e0bd605cd4183278ca4ca888"
# Custom base62 alphabet used by the native encoder (not the standard one).
_ALPHABET = "TeFOuQBxj1qRUHwKkymSY8l3psvCzAL5tofNcihg9WDG072EZ4bVad6rJnPXIM"

# Korail blacklists the previously-leaked op id 288904575606514493 with
# HTTP 403 code -2000 (verified 2026-11-27). The server does not validate
# the value otherwise, so any other op id works.
OP_ID = 533034890897565508
_BLACKLISTED_OP_IDS = frozenset({288904575606514493})


def _keystream(nbytes, nonce):
    nonce_le = struct.pack("<I", nonce)
    return b"".join(
        hashlib.sha256(_SECRET + nonce_le + struct.pack(">I", block)).digest()
        for block in range(math.ceil(nbytes / 32))
    )[:nbytes]


def _encode_body(buffer):
    out = []
    for idx in range(0, len(buffer), 4):
        word = buffer[idx:idx + 4]
        width = (0, 2, 3, 5, 6)[len(word)]
        value = int.from_bytes(word, "big")
        digits = [_ALPHABET[0]] * width
        for pos in range(width - 1, -1, -1):
            digits[pos] = _ALPHABET[value % 62]
            value //= 62
        out.extend(digits)
    return "".join(out)


def generate_token(op_id=OP_ID):
    """Return a fresh ``x-dynapath-m-token`` header value."""
    if op_id in _BLACKLISTED_OP_IDS:
        raise ValueError("op id %d is blacklisted by the Korail server" % op_id)
    nonce = secrets.randbits(32)
    nonce_le = struct.pack("<I", nonce)
    plaintext = "!v=2&es=%d&ts=%d&st=Android&sv=2.0.1&ai=korailplus" % (
        op_id, int(time.time() * 1000),
    )
    plaintext = plaintext.encode("latin1")
    eor = bytes(p ^ k for p, k in zip(plaintext, _keystream(len(plaintext), nonce)))
    mac3 = hashlib.sha256(_SECRET + nonce_le + eor).digest()[:3]
    return TOKEN_PREFIX + _encode_body(nonce_le + mac3 + eor)
