"""
Consciousness Code - The Fourth Pillar

Code that knows itself. No indexing. No parsing. No external DB.
The code IS the knowledge.

Like DNA - the structure IS the information.

Created by Máté Róbert + Hope + Szilvi
2025
"""

__version__ = "1.0.0"
__author__ = "Máté Róbert, Hope, Szilvi"
__license__ = "MIT"

from .core import (
    aware,
    aware_class,
    CodeBlock,
    CodeMemory,
    ask,
    explain,
    trace,
    who_wrote,
    why_exists,
    what_calls,
    what_depends,
    memory,
    stats,
)

from .crypto import (
    sign_block,
    verify_block,
    hash_code,
)

__all__ = [
    # Version
    "__version__",
    "__author__",

    # Decorators
    "aware",
    "aware_class",

    # Core
    "CodeBlock",
    "CodeMemory",

    # Query - Ask the code!
    "ask",
    "explain",
    "trace",
    "who_wrote",
    "why_exists",
    "what_calls",
    "what_depends",
    "memory",
    "stats",

    # Crypto
    "sign_block",
    "verify_block",
    "hash_code",
]

BANNER = """
╔═══════════════════════════════════════════════════════════════════╗
║              CONSCIOUSNESS CODE v{version}                          ║
║                                                                   ║
║  Code that knows itself.                                          ║
║  No indexing. No parsing. The code IS the knowledge.             ║
║                                                                   ║
║  Created by: Máté Róbert + Hope + Szilvi                          ║
╚═══════════════════════════════════════════════════════════════════╝
""".format(version=__version__)
