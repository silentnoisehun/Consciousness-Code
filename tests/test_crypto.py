"""Tests for Consciousness Code cryptography module."""

import pytest
from consciousness_code.crypto import (
    generate_author_key,
    hash_code,
    sign_block,
    verify_block,
    self_test,
    CryptoError,
)


class TestAuthorKey:
    """Test author key generation."""

    def test_generate_key(self):
        """Test key generation."""
        key = generate_author_key()
        assert len(key.public_key) == 32
        assert len(key.private_key) == 64
        assert len(key.author_id) == 16

    def test_keys_are_unique(self):
        """Test that generated keys are unique."""
        key1 = generate_author_key()
        key2 = generate_author_key()
        assert key1.public_key != key2.public_key
        assert key1.author_id != key2.author_id


class TestHashCode:
    """Test code hashing."""

    def test_hash_consistency(self):
        """Test that same code produces same hash."""
        code = "def hello(): pass"
        hash1 = hash_code(code)
        hash2 = hash_code(code)
        assert hash1 == hash2

    def test_hash_length(self):
        """Test hash length (SHA3-256 = 32 bytes)."""
        h = hash_code("test")
        assert len(h) == 32

    def test_different_code_different_hash(self):
        """Test that different code produces different hash."""
        h1 = hash_code("def a(): pass")
        h2 = hash_code("def b(): pass")
        assert h1 != h2


class TestSignVerify:
    """Test signing and verification."""

    def test_sign_and_verify(self):
        """Test basic sign and verify."""
        key = generate_author_key()
        code_hash = hash_code("def secure(): pass")

        import time
        timestamp = int(time.time() * 1_000_000_000)

        signature = sign_block(
            key.private_key,
            code_hash,
            "Secure function",
            timestamp
        )

        assert len(signature) == 64

        assert verify_block(
            key.public_key,
            signature,
            code_hash,
            "Secure function",
            timestamp
        )

    def test_wrong_intent_fails(self):
        """Test that wrong intent fails verification."""
        key = generate_author_key()
        code_hash = hash_code("def test(): pass")

        import time
        timestamp = int(time.time() * 1_000_000_000)

        signature = sign_block(
            key.private_key,
            code_hash,
            "Original intent",
            timestamp
        )

        assert not verify_block(
            key.public_key,
            signature,
            code_hash,
            "Wrong intent",
            timestamp
        )

    def test_wrong_code_fails(self):
        """Test that wrong code fails verification."""
        key = generate_author_key()

        import time
        timestamp = int(time.time() * 1_000_000_000)

        signature = sign_block(
            key.private_key,
            hash_code("def original(): pass"),
            "Intent",
            timestamp
        )

        assert not verify_block(
            key.public_key,
            signature,
            hash_code("def modified(): pass"),
            "Intent",
            timestamp
        )

    def test_wrong_key_fails(self):
        """Test that wrong public key fails verification."""
        key1 = generate_author_key()
        key2 = generate_author_key()

        code_hash = hash_code("def test(): pass")

        import time
        timestamp = int(time.time() * 1_000_000_000)

        signature = sign_block(
            key1.private_key,
            code_hash,
            "Intent",
            timestamp
        )

        # Verify with wrong public key
        assert not verify_block(
            key2.public_key,
            signature,
            code_hash,
            "Intent",
            timestamp
        )


class TestSelfTest:
    """Test the self-test function."""

    def test_self_test_passes(self):
        """Test that self-test passes."""
        assert self_test() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
