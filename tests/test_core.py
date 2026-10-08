"""Tests for Consciousness Code core module."""

import pytest

from consciousness_code import (
    ask,
    aware,
    aware_class,
    explain,
    memory,
    stats,
    who_wrote,
    why_exists,
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

    def test_by_author_by_tag(self):
        """Test finding code by author and by tag."""
        @aware(intent="Author search", author="unique_author_x", tags=["unique_tag_y"])
        def func_x():
            pass

        mem = memory()
        author_blocks = mem.by_author("unique_author_x")
        tag_blocks = mem.by_tag("unique_tag_y")

        assert len(author_blocks) >= 1
        assert func_x.__aware__.qualified_name in [b.qualified_name for b in author_blocks]
        assert len(tag_blocks) >= 1
        assert func_x.__aware__.qualified_name in [b.qualified_name for b in tag_blocks]

    def test_calls_and_depends(self):
        """Test explicit call and dependency tracking."""
        @aware(intent="Dependency block")
        def dep_func():
            pass

        dep_name = dep_func.__aware__.qualified_name

        @aware(intent="Caller block", calls=[dep_name], depends_on=[dep_name])
        def caller_func():
            pass

        caller_name = caller_func.__aware__.qualified_name

        mem = memory()
        dep_block = mem.get(dep_name)
        caller_block = mem.get(caller_name)

        assert dep_name in caller_block.calls
        assert dep_name in caller_block.depends_on
        assert caller_name in dep_block.called_by
        assert caller_name in dep_block.depended_by


class TestCryoStasis:
    """Test freezing and thawing code memory from disk (binary & JSON)."""

    def test_freeze_and_thaw_binary(self, tmp_path):
        """Test native binary freezing memory, clearing memory, and thawing from disk."""
        from consciousness_code import freeze_binary, thaw_binary

        @aware(intent="Binary Cryo function", author="binary_author", tags=["binary_stasis"])
        def binary_stasis_func():
            pass

        stasis_file = tmp_path / "cryo_test.bin"
        saved_path = freeze_binary(stasis_file)
        assert saved_path == str(stasis_file)

        mem = memory()
        mem.clear()
        assert len(mem.all()) == 0

        restored_count = thaw_binary(stasis_file)
        assert restored_count >= 1

        results = ask("binary_author")
        assert len(results) >= 1
        assert results[0].intent == "Binary Cryo function"

    def test_freeze_and_thaw_json(self, tmp_path):
        """Test JSON freezing memory, clearing memory, and thawing from disk."""
        from consciousness_code import freeze, thaw

        @aware(intent="JSON Cryo function", author="json_author")
        def json_stasis_func():
            pass

        stasis_file = tmp_path / "cryo_test.json"
        saved_path = freeze(stasis_file, binary=False)
        assert saved_path == str(stasis_file)

        mem = memory()
        mem.clear()
        assert len(mem.all()) == 0

        restored_count = thaw(stasis_file, binary=False)
        assert restored_count >= 1

        results = ask("json_author")
        assert len(results) >= 1

    def test_thaw_invalid_binary_file(self, tmp_path):
        """Test thawing tampered binary cryo stasis file raises ValueError."""
        from consciousness_code import freeze_binary, thaw_binary

        @aware(intent="Binary Cryo tamper test")
        def tamper_func():
            pass

        stasis_file = tmp_path / "tampered.bin"
        freeze_binary(stasis_file)

        # Tamper the file content bytearray
        content = bytearray(stasis_file.read_bytes())
        content[-1] ^= 0xFF  # Corrupt last byte
        stasis_file.write_bytes(content)

        with pytest.raises(ValueError, match="integrity check failed"):
            thaw_binary(stasis_file)

    def test_thaw_invalid_json_file(self, tmp_path):
        """Test thawing tampered json cryo stasis file raises ValueError."""
        from consciousness_code import freeze, thaw

        @aware(intent="JSON Cryo tamper test")
        def tamper_json():
            pass

        stasis_file = tmp_path / "tampered.json"
        freeze(stasis_file, binary=False)

        # Tamper the file content
        content = stasis_file.read_text(encoding="utf-8")
        stasis_file.write_text(content.replace("JSON Cryo tamper test", "Tampered intent"), encoding="utf-8")

        with pytest.raises(ValueError, match="integrity check failed"):
            thaw(stasis_file, binary=False)


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
