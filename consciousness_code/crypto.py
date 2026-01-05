"""
Self-Aware Code - Cryptography Module

Sign and verify code blocks.
Immutable proof of authorship.

Created by Máté Róbert + Hope
"""

import hashlib
import secrets
import struct
import time
from dataclasses import dataclass
from typing import Optional, Tuple


class CryptoError(Exception):
    """Cryptographic operation failed."""
    pass


# Ed25519 curve parameters (simplified - use 'cryptography' in production)
ED25519_P = 2**255 - 19
ED25519_L = 2**252 + 27742317777372353535851937790883648493
ED25519_D = -121665 * pow(121666, ED25519_P - 2, ED25519_P) % ED25519_P
ED25519_I = pow(2, (ED25519_P - 1) // 4, ED25519_P)
ED25519_BY = 4 * pow(5, ED25519_P - 2, ED25519_P) % ED25519_P


def _recover_x(y: int, sign: int) -> Optional[int]:
    """Recover x coordinate from y coordinate on Ed25519 curve."""
    if y >= ED25519_P:
        return None

    y2 = y * y % ED25519_P
    x2 = (y2 - 1) * pow(ED25519_D * y2 + 1, ED25519_P - 2, ED25519_P) % ED25519_P

    if x2 == 0:
        if sign:
            return None
        return 0

    x = pow(x2, (ED25519_P + 3) // 8, ED25519_P)

    if (x * x - x2) % ED25519_P != 0:
        x = x * ED25519_I % ED25519_P

    if (x * x - x2) % ED25519_P != 0:
        return None

    if x % 2 != sign:
        x = ED25519_P - x

    return x


ED25519_BX = _recover_x(ED25519_BY, 0)
ED25519_B = (ED25519_BX, ED25519_BY, 1, ED25519_BX * ED25519_BY % ED25519_P)


def _point_add(P, Q):
    """Add two points on Ed25519 curve."""
    x1, y1, z1, t1 = P
    x2, y2, z2, t2 = Q

    a = (y1 - x1) * (y2 - x2) % ED25519_P
    b = (y1 + x1) * (y2 + x2) % ED25519_P
    c = 2 * ED25519_D * t1 * t2 % ED25519_P
    d = 2 * z1 * z2 % ED25519_P

    e = b - a
    f = d - c
    g = d + c
    h = b + a

    x3 = e * f % ED25519_P
    y3 = g * h % ED25519_P
    z3 = f * g % ED25519_P
    t3 = e * h % ED25519_P

    return (x3, y3, z3, t3)


def _scalar_mult(s: int, P) -> tuple:
    """Multiply point by scalar on Ed25519."""
    Q = (0, 1, 1, 0)  # Identity

    while s > 0:
        if s & 1:
            Q = _point_add(Q, P)
        P = _point_add(P, P)
        s >>= 1

    return Q


def _point_compress(P) -> bytes:
    """Compress point to 32 bytes."""
    x, y, z, _ = P
    zi = pow(z, ED25519_P - 2, ED25519_P)
    x = x * zi % ED25519_P
    y = y * zi % ED25519_P
    return (y | ((x & 1) << 255)).to_bytes(32, 'little')


def _point_decompress(s: bytes) -> tuple:
    """Decompress 32 bytes to point."""
    if len(s) != 32:
        raise CryptoError("Invalid point length")

    y = int.from_bytes(s, 'little')
    sign = y >> 255
    y &= (1 << 255) - 1

    x = _recover_x(y, sign)
    if x is None:
        raise CryptoError("Invalid point")

    return (x, y, 1, x * y % ED25519_P)


def _sha512(data: bytes) -> bytes:
    """SHA-512 hash."""
    return hashlib.sha512(data).digest()


def _clamp(k: bytes) -> int:
    """Clamp scalar for Ed25519."""
    k_list = list(k)
    k_list[0] &= 248
    k_list[31] &= 127
    k_list[31] |= 64
    return int.from_bytes(bytes(k_list), 'little')


@dataclass
class AuthorKey:
    """Author's cryptographic identity."""
    public_key: bytes
    private_key: bytes
    author_id: bytes

    def __repr__(self) -> str:
        return f"AuthorKey(id={self.author_id.hex()[:16]}...)"


def generate_author_key() -> AuthorKey:
    """Generate a new author identity."""
    seed = secrets.token_bytes(32)

    h = _sha512(seed)
    a = _clamp(h[:32])

    A = _scalar_mult(a, ED25519_B)
    public_key = _point_compress(A)

    private_key = seed + public_key

    author_id = hashlib.sha3_256(public_key).digest()[:16]

    return AuthorKey(
        public_key=public_key,
        private_key=private_key,
        author_id=author_id
    )


def hash_code(source: str) -> bytes:
    """
    Hash source code using SHA3-256.

    This is the code's cryptographic identity.
    """
    return hashlib.sha3_256(source.encode()).digest()


def sign_block(
    private_key: bytes,
    code_hash: bytes,
    intent: str,
    timestamp: Optional[int] = None
) -> bytes:
    """
    Sign a code block.

    Creates cryptographic proof of authorship.
    """
    if len(private_key) != 64:
        raise CryptoError("Private key must be 64 bytes")

    if timestamp is None:
        timestamp = int(time.time() * 1_000_000_000)

    # Create message: hash || intent || timestamp
    message = code_hash + intent.encode() + struct.pack('>Q', timestamp)

    seed = private_key[:32]
    public_key = private_key[32:]

    h = _sha512(seed)
    a = _clamp(h[:32])
    prefix = h[32:]

    r = int.from_bytes(_sha512(prefix + message), 'little') % ED25519_L

    R = _scalar_mult(r, ED25519_B)
    R_bytes = _point_compress(R)

    k = int.from_bytes(_sha512(R_bytes + public_key + message), 'little') % ED25519_L

    s = (r + k * a) % ED25519_L

    return R_bytes + s.to_bytes(32, 'little')


def verify_block(
    public_key: bytes,
    signature: bytes,
    code_hash: bytes,
    intent: str,
    timestamp: int
) -> bool:
    """
    Verify a code block's signature.

    Returns True if the code was signed by the author.
    """
    if len(public_key) != 32:
        raise CryptoError("Public key must be 32 bytes")
    if len(signature) != 64:
        raise CryptoError("Signature must be 64 bytes")

    try:
        message = code_hash + intent.encode() + struct.pack('>Q', timestamp)

        A = _point_decompress(public_key)
        R_bytes = signature[:32]
        R = _point_decompress(R_bytes)
        s = int.from_bytes(signature[32:], 'little')

        if s >= ED25519_L:
            return False

        k = int.from_bytes(_sha512(R_bytes + public_key + message), 'little') % ED25519_L

        sB = _scalar_mult(s, ED25519_B)
        kA = _scalar_mult(k, A)
        RkA = _point_add(R, kA)

        return _point_compress(sB) == _point_compress(RkA)
    except Exception:
        return False


@dataclass
class SignedBlock:
    """A cryptographically signed code block."""
    code_hash: bytes
    intent: str
    author_id: bytes
    timestamp: int
    signature: bytes

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        intent_bytes = self.intent.encode()
        return (
            self.code_hash +
            struct.pack('>H', len(intent_bytes)) +
            intent_bytes +
            self.author_id +
            struct.pack('>Q', self.timestamp) +
            self.signature
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> 'SignedBlock':
        """Deserialize from bytes."""
        code_hash = data[:32]
        intent_len = struct.unpack('>H', data[32:34])[0]
        intent = data[34:34+intent_len].decode()
        author_id = data[34+intent_len:50+intent_len]
        timestamp = struct.unpack('>Q', data[50+intent_len:58+intent_len])[0]
        signature = data[58+intent_len:122+intent_len]

        return cls(
            code_hash=code_hash,
            intent=intent,
            author_id=author_id,
            timestamp=timestamp,
            signature=signature
        )


def self_test() -> bool:
    """Run cryptographic self-tests."""
    # Test key generation
    key = generate_author_key()
    assert len(key.public_key) == 32
    assert len(key.private_key) == 64
    assert len(key.author_id) == 16

    # Test signing
    code_hash = hash_code("def hello(): pass")
    timestamp = int(time.time() * 1_000_000_000)
    signature = sign_block(key.private_key, code_hash, "Test", timestamp)
    assert len(signature) == 64

    # Test verification
    assert verify_block(key.public_key, signature, code_hash, "Test", timestamp)
    assert not verify_block(key.public_key, signature, code_hash, "Wrong", timestamp)

    return True


if __name__ == "__main__":
    print("Running crypto self-tests...")
    if self_test():
        print("All tests passed!")
    else:
        print("Tests failed!")
        exit(1)
