"""
Self-Aware Code - Core Module

The code knows itself. No indexing required.

Created by Máté Róbert + Hope
"""

import functools
import hashlib
import inspect
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Optional,
    TypeVar,
    cast,
)

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class CodeBlock:
    """
    A self-aware piece of code.

    Contains all knowledge about itself:
    - Who wrote it
    - Why it exists
    - What it does
    - What it connects to
    - Cryptographic identity
    """

    # Identity
    name: str
    qualified_name: str
    hash: str

    # Knowledge
    author: str = "unknown"
    intent: str = ""
    description: str = ""

    # Source
    source_code: str = ""
    file_path: str = ""
    line_number: int = 0

    # Timestamps
    created_at: float = field(default_factory=time.time)

    # Relationships (discovered at runtime)
    calls: set[str] = field(default_factory=set)
    called_by: set[str] = field(default_factory=set)
    depends_on: set[str] = field(default_factory=set)
    depended_by: set[str] = field(default_factory=set)

    # Tags for semantic search
    tags: set[str] = field(default_factory=set)

    # The actual callable
    _callable: Callable | None = field(default=None, repr=False)

    def explain(self) -> str:
        """The code explains itself."""
        parts = [
            f"=== {self.qualified_name} ===",
            "",
            f"Intent: {self.intent or 'Not specified'}",
            f"Description: {self.description or 'Not specified'}",
            f"Author: {self.author}",
            "",
            f"Location: {self.file_path}:{self.line_number}",
            f"Hash: {self.hash[:16]}...",
            "",
        ]

        if self.calls:
            parts.append(f"Calls: {', '.join(sorted(self.calls))}")
        if self.called_by:
            parts.append(f"Called by: {', '.join(sorted(self.called_by))}")
        if self.tags:
            parts.append(f"Tags: {', '.join(sorted(self.tags))}")

        return "\n".join(parts)

    def matches(self, query: str) -> bool:
        """Check if this code block matches a search query."""
        query_lower = query.lower()

        # Check all text fields
        searchable = [
            self.name,
            self.qualified_name,
            self.intent,
            self.description,
            self.author,
            self.source_code,
            *self.tags,
        ]

        for text in searchable:
            if query_lower in text.lower():
                return True

        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert code block to serializable dictionary."""
        return {
            "name": self.name,
            "qualified_name": self.qualified_name,
            "hash": self.hash,
            "author": self.author,
            "intent": self.intent,
            "description": self.description,
            "source_code": self.source_code,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "created_at": self.created_at,
            "calls": sorted(self.calls),
            "called_by": sorted(self.called_by),
            "depends_on": sorted(self.depends_on),
            "depended_by": sorted(self.depended_by),
            "tags": sorted(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'CodeBlock':
        """Reconstruct code block from dictionary."""
        return cls(
            name=data.get("name", ""),
            qualified_name=data.get("qualified_name", ""),
            hash=data.get("hash", ""),
            author=data.get("author", "unknown"),
            intent=data.get("intent", ""),
            description=data.get("description", ""),
            source_code=data.get("source_code", ""),
            file_path=data.get("file_path", ""),
            line_number=data.get("line_number", 0),
            created_at=data.get("created_at", time.time()),
            calls=set(data.get("calls", [])),
            called_by=set(data.get("called_by", [])),
            depends_on=set(data.get("depends_on", [])),
            depended_by=set(data.get("depended_by", [])),
            tags=set(data.get("tags", [])),
        )


class CodeMemory:
    """
    Global memory of all self-aware code.

    No indexing. No database. The code registers itself.
    When you import a module, its aware code announces itself.
    """

    _instance: Optional['CodeMemory'] = None
    _blocks: dict[str, CodeBlock]
    _by_file: dict[str, list[str]]
    _by_author: dict[str, list[str]]
    _by_tag: dict[str, list[str]]

    def __new__(cls) -> 'CodeMemory':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._blocks = {}
            cls._instance._by_file = {}
            cls._instance._by_author = {}
            cls._instance._by_tag = {}
        return cls._instance

    def register(self, block: CodeBlock) -> None:
        """A code block announces itself to memory."""
        self._blocks[block.qualified_name] = block

        # Organize by file
        if block.file_path:
            if block.file_path not in self._by_file:
                self._by_file[block.file_path] = []
            if block.qualified_name not in self._by_file[block.file_path]:
                self._by_file[block.file_path].append(block.qualified_name)

        # Organize by author
        if block.author:
            if block.author not in self._by_author:
                self._by_author[block.author] = []
            if block.qualified_name not in self._by_author[block.author]:
                self._by_author[block.author].append(block.qualified_name)

        # Organize by tags
        for tag in block.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            if block.qualified_name not in self._by_tag[tag]:
                self._by_tag[tag].append(block.qualified_name)

        # Update bidirectional relationships for calls and depends_on
        for call_target in block.calls:
            if call_target in self._blocks:
                self._blocks[call_target].called_by.add(block.qualified_name)

        for dep_target in block.depends_on:
            if dep_target in self._blocks:
                self._blocks[dep_target].depended_by.add(block.qualified_name)

        for other in self._blocks.values():
            if block.qualified_name in other.calls:
                block.called_by.add(other.qualified_name)
            if block.qualified_name in other.depends_on:
                block.depended_by.add(other.qualified_name)

    def get(self, name: str) -> CodeBlock | None:
        """Get a code block by name."""
        return self._blocks.get(name)

    def ask(self, question: str) -> list[CodeBlock]:
        """
        Ask the code a question.

        No parsing. No indexing. The code knows itself.
        """
        results = []

        for block in self._blocks.values():
            if block.matches(question):
                results.append(block)

        return results

    def by_author(self, author: str) -> list[CodeBlock]:
        """Find all code written by an author."""
        names = self._by_author.get(author, [])
        return [self._blocks[n] for n in names]

    def by_file(self, file_path: str) -> list[CodeBlock]:
        """Find all code in a file."""
        names = self._by_file.get(file_path, [])
        return [self._blocks[n] for n in names]

    def by_tag(self, tag: str) -> list[CodeBlock]:
        """Find all code with a tag."""
        names = self._by_tag.get(tag, [])
        return [self._blocks[n] for n in names]

    def all(self) -> list[CodeBlock]:
        """Get all known code blocks."""
        return list(self._blocks.values())

    def trace(self, name: str, depth: int = 3) -> dict[str, Any]:
        """
        Trace the call graph from a function.

        The code knows what it calls and what calls it.
        """
        block = self.get(name)
        if not block:
            return {"error": f"Unknown: {name}"}

        def trace_calls(n: str, d: int) -> dict:
            if d <= 0:
                return {"name": n, "calls": "..."}

            b = self.get(n)
            if not b:
                return {"name": n, "calls": []}

            return {
                "name": n,
                "intent": b.intent,
                "calls": [trace_calls(c, d-1) for c in b.calls if self.get(c)]
            }

        return trace_calls(name, depth)

    def stats(self) -> dict[str, Any]:
        """Statistics about the code memory."""
        return {
            "total_blocks": len(self._blocks),
            "files": len(self._by_file),
            "authors": len(self._by_author),
            "tags": len(self._by_tag),
        }

    def clear(self) -> None:
        """Clear all registered code blocks from memory."""
        self._blocks.clear()
        self._by_file.clear()
        self._by_author.clear()
        self._by_tag.clear()

    def freeze(self, filepath: str | Path = "cryo_stasis.json") -> str:
        """
        Freeze (persist) code memory into cryo stasis JSON file.

        Returns path to frozen stasis file.
        """
        path = Path(filepath)
        data = {
            "version": "1.0.0",
            "frozen_at": time.time(),
            "blocks": [b.to_dict() for b in self._blocks.values()],
        }
        content = json.dumps(data, indent=2)
        checksum = hashlib.sha3_256(content.encode()).hexdigest()
        payload = {
            "checksum": checksum,
            "data": data,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path)

    def thaw(self, filepath: str | Path = "cryo_stasis.json") -> int:
        """
        Thaw (restore) code memory from cryo stasis JSON file on demand.

        Returns number of code blocks restored.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Cryo stasis file not found: {path}")

        payload = json.loads(path.read_text(encoding="utf-8"))
        checksum = payload.get("checksum")
        data = payload.get("data", {})
        expected_checksum = hashlib.sha3_256(json.dumps(data, indent=2).encode()).hexdigest()

        if checksum != expected_checksum:
            raise ValueError("Cryo stasis file integrity check failed! File may be tampered.")

        blocks_data = data.get("blocks", [])
        count = 0
        for block_dict in blocks_data:
            block = CodeBlock.from_dict(block_dict)
            self.register(block)
            count += 1

        return count


# Global memory instance
_memory = CodeMemory()


def _compute_hash(source: str) -> str:
    """Compute SHA3-256 hash of source code."""
    return hashlib.sha3_256(source.encode()).hexdigest()


def aware(
    intent: str = "",
    author: str = "unknown",
    tags: list[str] | None = None,
    description: str = "",
    calls: list[str] | None = None,
    depends_on: list[str] | None = None,
) -> Callable[[F], F]:
    """
    Make a function self-aware.

    The function will know:
    - Who wrote it
    - Why it exists
    - What it does
    - Its cryptographic identity

    Example:
        @aware(
            intent="Authenticate users securely",
            author="mate",
            tags=["auth", "security"]
        )
        def login(user, password):
            ...

        # Later, ask the code:
        login.__aware__.explain()
        # The function tells you about itself!
    """
    def decorator(func: F) -> F:
        # Get source info
        try:
            source = inspect.getsource(func)
            file_path = inspect.getfile(func)
            lines, line_number = inspect.getsourcelines(func)
        except (OSError, TypeError):
            source = ""
            file_path = ""
            line_number = 0

        # Create code block
        block = CodeBlock(
            name=func.__name__,
            qualified_name=f"{func.__module__}.{func.__qualname__}",
            hash=_compute_hash(source),
            author=author,
            intent=intent,
            description=description or func.__doc__ or "",
            source_code=source,
            file_path=file_path,
            line_number=line_number,
            calls=set(calls or []),
            depends_on=set(depends_on or []),
            tags=set(tags or []),
            _callable=func,
        )

        # Register with global memory
        _memory.register(block)

        # Wrap function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Attach awareness
        setattr(wrapper, '__aware__', block)

        return cast(F, wrapper)

    return decorator


def aware_class(
    intent: str = "",
    author: str = "unknown",
    tags: list[str] | None = None,
    description: str = "",
    calls: list[str] | None = None,
    depends_on: list[str] | None = None,
) -> Callable[[type], type]:
    """
    Make a class self-aware.

    All methods become aware automatically.
    """
    def decorator(cls: type) -> type:
        # Get source info
        try:
            source = inspect.getsource(cls)
            file_path = inspect.getfile(cls)
            lines, line_number = inspect.getsourcelines(cls)
        except (OSError, TypeError):
            source = ""
            file_path = ""
            line_number = 0

        # Create code block for class
        block = CodeBlock(
            name=cls.__name__,
            qualified_name=f"{cls.__module__}.{cls.__qualname__}",
            hash=_compute_hash(source),
            author=author,
            intent=intent,
            description=description or cls.__doc__ or "",
            source_code=source,
            file_path=file_path,
            line_number=line_number,
            calls=set(calls or []),
            depends_on=set(depends_on or []),
            tags=set(tags or []),
        )

        # Register class
        _memory.register(block)

        # Attach awareness
        setattr(cls, '__aware__', block)

        # Make methods aware too
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not name.startswith('_'):
                method_block = CodeBlock(
                    name=name,
                    qualified_name=f"{cls.__module__}.{cls.__qualname__}.{name}",
                    hash=_compute_hash(inspect.getsource(method) if hasattr(method, '__code__') else ""),
                    author=author,
                    intent=f"Method of {cls.__name__}",
                    tags=set(tags or []),
                    _callable=method,
                )
                _memory.register(method_block)
                block.calls.add(method_block.qualified_name)

        return cls

    return decorator


# ============================================================================
# Query Functions - Ask the code!
# ============================================================================

def ask(question: str) -> list[CodeBlock]:
    """
    Ask the code a question.

    No indexing. No parsing. The code knows itself.

    Example:
        results = ask("authentication")
        for code in results:
            print(code.explain())
    """
    return _memory.ask(question)


def explain(name: str) -> str:
    """
    Ask a specific function to explain itself.

    Example:
        print(explain("mymodule.login"))
    """
    block = _memory.get(name)
    if block:
        return block.explain()
    return f"Unknown: {name}"


def trace(name: str, depth: int = 3) -> dict[str, Any]:
    """
    Trace the call graph from a function.

    Example:
        graph = trace("mymodule.main")
        # Returns the call tree
    """
    return _memory.trace(name, depth)


def who_wrote(name: str) -> str:
    """Ask who wrote a piece of code."""
    block = _memory.get(name)
    if block:
        return block.author
    return "unknown"


def why_exists(name: str) -> str:
    """Ask why a piece of code exists."""
    block = _memory.get(name)
    if block:
        return block.intent
    return "unknown"


def what_calls(name: str) -> set[str]:
    """Ask what functions a piece of code calls."""
    block = _memory.get(name)
    if block:
        return block.calls
    return set()


def what_depends(name: str) -> set[str]:
    """Ask what depends on a piece of code."""
    block = _memory.get(name)
    if block:
        return block.depended_by
    return set()


def memory() -> CodeMemory:
    """Get the global code memory."""
    return _memory


def stats() -> dict[str, Any]:
    """Get statistics about the code memory."""
    return _memory.stats()


def freeze(filepath: str | Path = "cryo_stasis.json") -> str:
    """Freeze code memory to cryo stasis disk storage."""
    return _memory.freeze(filepath)


def thaw(filepath: str | Path = "cryo_stasis.json") -> int:
    """Thaw code memory from cryo stasis disk storage on call."""
    return _memory.thaw(filepath)
