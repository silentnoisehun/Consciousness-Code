"""
Self-Aware Code - Core Module

The code knows itself. No indexing required.

Created by Máté Róbert + Hope
"""

import hashlib
import inspect
import functools
import time
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    TypeVar,
    Union,
)
from pathlib import Path


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
    calls: Set[str] = field(default_factory=set)
    called_by: Set[str] = field(default_factory=set)
    depends_on: Set[str] = field(default_factory=set)
    depended_by: Set[str] = field(default_factory=set)

    # Tags for semantic search
    tags: Set[str] = field(default_factory=set)

    # The actual callable
    _callable: Optional[Callable] = field(default=None, repr=False)

    def explain(self) -> str:
        """The code explains itself."""
        parts = [
            f"=== {self.qualified_name} ===",
            f"",
            f"Intent: {self.intent or 'Not specified'}",
            f"Description: {self.description or 'Not specified'}",
            f"Author: {self.author}",
            f"",
            f"Location: {self.file_path}:{self.line_number}",
            f"Hash: {self.hash[:16]}...",
            f"",
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


class CodeMemory:
    """
    Global memory of all self-aware code.

    No indexing. No database. The code registers itself.
    When you import a module, its aware code announces itself.
    """

    _instance: Optional['CodeMemory'] = None

    def __new__(cls) -> 'CodeMemory':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._blocks: Dict[str, CodeBlock] = {}
            cls._instance._by_file: Dict[str, List[str]] = {}
            cls._instance._by_author: Dict[str, List[str]] = {}
            cls._instance._by_tag: Dict[str, List[str]] = {}
        return cls._instance

    def register(self, block: CodeBlock) -> None:
        """A code block announces itself to memory."""
        self._blocks[block.qualified_name] = block

        # Organize by file
        if block.file_path:
            if block.file_path not in self._by_file:
                self._by_file[block.file_path] = []
            self._by_file[block.file_path].append(block.qualified_name)

        # Organize by author
        if block.author:
            if block.author not in self._by_author:
                self._by_author[block.author] = []
            self._by_author[block.author].append(block.qualified_name)

        # Organize by tags
        for tag in block.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(block.qualified_name)

    def get(self, name: str) -> Optional[CodeBlock]:
        """Get a code block by name."""
        return self._blocks.get(name)

    def ask(self, question: str) -> List[CodeBlock]:
        """
        Ask the code a question.

        No parsing. No indexing. The code knows itself.
        """
        results = []

        for block in self._blocks.values():
            if block.matches(question):
                results.append(block)

        return results

    def by_author(self, author: str) -> List[CodeBlock]:
        """Find all code written by an author."""
        names = self._by_author.get(author, [])
        return [self._blocks[n] for n in names]

    def by_file(self, file_path: str) -> List[CodeBlock]:
        """Find all code in a file."""
        names = self._by_file.get(file_path, [])
        return [self._blocks[n] for n in names]

    def by_tag(self, tag: str) -> List[CodeBlock]:
        """Find all code with a tag."""
        names = self._by_tag.get(tag, [])
        return [self._blocks[n] for n in names]

    def all(self) -> List[CodeBlock]:
        """Get all known code blocks."""
        return list(self._blocks.values())

    def trace(self, name: str, depth: int = 3) -> Dict[str, Any]:
        """
        Trace the call graph from a function.

        The code knows what it calls and what calls it.
        """
        block = self.get(name)
        if not block:
            return {"error": f"Unknown: {name}"}

        def trace_calls(n: str, d: int) -> Dict:
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

    def stats(self) -> Dict[str, Any]:
        """Statistics about the code memory."""
        return {
            "total_blocks": len(self._blocks),
            "files": len(self._by_file),
            "authors": len(self._by_author),
            "tags": len(self._by_tag),
        }


# Global memory instance
_memory = CodeMemory()


def _compute_hash(source: str) -> str:
    """Compute SHA3-256 hash of source code."""
    return hashlib.sha3_256(source.encode()).hexdigest()


def aware(
    intent: str = "",
    author: str = "unknown",
    tags: Optional[List[str]] = None,
    description: str = "",
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
        wrapper.__aware__ = block

        return wrapper

    return decorator


def aware_class(
    intent: str = "",
    author: str = "unknown",
    tags: Optional[List[str]] = None,
    description: str = "",
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
            tags=set(tags or []),
        )

        # Register class
        _memory.register(block)

        # Attach awareness
        cls.__aware__ = block

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

def ask(question: str) -> List[CodeBlock]:
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


def trace(name: str, depth: int = 3) -> Dict[str, Any]:
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


def what_calls(name: str) -> Set[str]:
    """Ask what functions a piece of code calls."""
    block = _memory.get(name)
    if block:
        return block.calls
    return set()


def what_depends(name: str) -> Set[str]:
    """Ask what depends on a piece of code."""
    block = _memory.get(name)
    if block:
        return block.depended_by
    return set()


def memory() -> CodeMemory:
    """Get the global code memory."""
    return _memory


def stats() -> Dict[str, Any]:
    """Get statistics about the code memory."""
    return _memory.stats()
