"""Tests for Consciousness Code core module."""

import pytest
from consciousness_code import (
    aware,
    aware_class,
    ask,
    explain,
    who_wrote,
    why_exists,
    memory,
    stats,
)


class TestAwareDecorator:
    """Test the @aware decorator."""

    def test_basic_aware(self):
        """Test basic aware decorator."""
        @aware(intent="Test function", author="test")
        def test_func():
            return 42

        assert test_func() == 42
        assert hasattr(test_func, '__aware__')
        assert test_func.__aware__.intent == "Test function"
        assert test_func.__aware__.author == "test"

    def test_aware_with_tags(self):
        """Test aware decorator with tags."""
        @aware(intent="Tagged", tags=["tag1", "tag2"])
        def tagged_func():
            pass

        assert "tag1" in tagged_func.__aware__.tags
        assert "tag2" in tagged_func.__aware__.tags

    def test_aware_hash(self):
        """Test that aware functions have a hash."""
        @aware(intent="Hashable")
        def hash_test():
            pass

        assert hash_test.__aware__.hash
        assert len(hash_test.__aware__.hash) == 64  # SHA3-256 hex

    def test_aware_preserves_docstring(self):
        """Test that docstrings are preserved."""
        @aware(intent="Documented")
        def documented():
            """This is the docstring."""
            pass

        assert documented.__doc__ == "This is the docstring."


class TestAwareClass:
    """Test the @aware_class decorator."""

    def test_basic_aware_class(self):
        """Test basic aware class."""
        @aware_class(intent="Test class", author="test")
        class TestClass:
            def method(self):
                return 1

        assert hasattr(TestClass, '__aware__')
        assert TestClass.__aware__.intent == "Test class"


class TestQueryFunctions:
    """Test query functions."""

    def test_ask(self):
        """Test asking the code."""
        @aware(intent="Searchable function", tags=["search_test"])
        def searchable():
            pass

        results = ask("search_test")
        assert len(results) > 0

    def test_who_wrote(self):
        """Test who_wrote query."""
        @aware(intent="Authored", author="known_author")
        def authored_func():
            pass

        # Get qualified name
        name = authored_func.__aware__.qualified_name
        assert who_wrote(name) == "known_author"

    def test_why_exists(self):
        """Test why_exists query."""
        @aware(intent="Exists for testing")
        def exists_func():
            pass

        name = exists_func.__aware__.qualified_name
        assert why_exists(name) == "Exists for testing"


class TestCodeMemory:
    """Test CodeMemory singleton."""

    def test_memory_is_singleton(self):
        """Test that memory is a singleton."""
        mem1 = memory()
        mem2 = memory()
        assert mem1 is mem2

    def test_stats(self):
        """Test statistics."""
        s = stats()
        assert "total_blocks" in s
        assert "files" in s
        assert "authors" in s


class TestExplain:
    """Test code self-explanation."""

    def test_explain_returns_string(self):
        """Test explain returns a string."""
        @aware(intent="Explainable", author="tester")
        def explainable():
            pass

        name = explainable.__aware__.qualified_name
        explanation = explain(name)

        assert isinstance(explanation, str)
        assert "Explainable" in explanation
        assert "tester" in explanation

    def test_explain_unknown(self):
        """Test explain with unknown function."""
        result = explain("nonexistent.function")
        assert "Unknown" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
