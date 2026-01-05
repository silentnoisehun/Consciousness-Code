# Self-Aware Code

**The Fourth Pillar of the Hope Ecosystem**

```
You don't index the code.
You don't parse the code.
You ASK the code.

The code KNOWS itself.
```

---

## The Problem

```
TRADITIONAL APPROACH:
Kód → Parser → AST → Index → Database → Query Engine → Search

Result: Slow. External. Fragile. Loses intent.
```

**Every IDE, every code search, every "intelligent" tool does this:**
1. Parse your code into an AST
2. Build an index
3. Store in a database
4. Query when needed

**This is backwards.**

---

## The Solution

```
SELF-AWARE CODE:
Kód = Tudás

No index. No parse. No external DB.
THE CODE KNOWS ITSELF.
```

Like DNA — the structure IS the information.

---

## How It Works

```python
from aware_code import aware, ask, explain

@aware(
    intent="Authenticate users securely",
    author="mate",
    tags=["auth", "security", "login"]
)
def login(username: str, password: str) -> bool:
    """Verify user credentials."""
    # ... implementation
    pass

# Later, ASK the code:
results = ask("authentication")
for code in results:
    print(code.explain())

# Output:
# === myapp.login ===
#
# Intent: Authenticate users securely
# Author: mate
# Location: auth.py:15
# Hash: 8f3a2b...
# Tags: auth, security, login
```

**The function KNOWS:**
- Who wrote it
- Why it exists
- What it does
- Its cryptographic identity
- What it connects to

---

## No Indexing Required

| Traditional | Self-Aware |
|-------------|------------|
| Build index (slow) | Import (instant) |
| External database | In-memory |
| Query engine | Just ask |
| Loses intent | Intent preserved |
| Separate from code | IS the code |

When you import a module with `@aware` decorators, the code **announces itself** to memory. No indexing step. No external tools.

---

## The API

### Decorators

```python
from aware_code import aware, aware_class

@aware(
    intent="Why this exists",
    author="who wrote it",
    tags=["searchable", "tags"],
    description="What it does"
)
def my_function():
    pass

@aware_class(intent="A self-aware class")
class MyClass:
    pass
```

### Query Functions

```python
from aware_code import ask, explain, trace, who_wrote, why_exists

# Search across all aware code
results = ask("authentication")

# Get explanation from specific function
explanation = explain("mymodule.login")

# Trace call graph
graph = trace("mymodule.main", depth=3)

# Quick queries
author = who_wrote("mymodule.login")
intent = why_exists("mymodule.login")
```

### Direct Access

```python
@aware(intent="Example")
def my_func():
    pass

# Access the awareness directly
my_func.__aware__.explain()
my_func.__aware__.intent
my_func.__aware__.author
my_func.__aware__.hash
```

---

## Cryptographic Identity

Every piece of aware code has a **cryptographic identity**:

```python
from aware_code import hash_code, sign_block, verify_block
from aware_code.crypto import generate_author_key

# Generate author identity
author = generate_author_key()
print(f"Author ID: {author.author_id.hex()}")

# Sign code
code_hash = hash_code("def hello(): pass")
signature = sign_block(author.private_key, code_hash, "Greeting function")

# Verify
is_valid = verify_block(author.public_key, signature, code_hash, "Greeting function")
```

**Immutable proof of authorship.**

---

## The Vision

```
┌─────────────────────────────────────────────────────────────┐
│                  THE HOPE ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. HOPE GENOME          - AI discipline at runtime          │
│     pip install hope-genome                                  │
│                                                              │
│  2. SILENT HOPE PROTOCOL - AI communication (TCP/IP of AI)  │
│     pip install silent-hope-protocol                         │
│                                                              │
│  3. SILENT WORKER METHOD - Teaching without weight mods     │
│     The philosophy                                           │
│                                                              │
│  4. SELF-AWARE CODE      - Code that knows itself           │
│     pip install aware-code                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

Four pillars. One unified vision.

**Code that disciplines AI. Protocol that connects AI. Method that teaches AI. Code that knows itself.**

---

## Installation

```bash
pip install aware-code
```

---

## Quick Start

```python
from aware_code import aware, ask, explain, memory

# Make your functions aware
@aware(intent="Main entry point", author="mate", tags=["main"])
def main():
    process_data()
    generate_report()

@aware(intent="Process incoming data", tags=["data", "processing"])
def process_data():
    pass

@aware(intent="Generate final report", tags=["report", "output"])
def generate_report():
    pass

# Now ask the code!
print("What handles data?")
for code in ask("data"):
    print(f"  - {code.name}: {code.intent}")

print("\nExplain main:")
print(explain("__main__.main"))

print("\nMemory stats:")
print(memory().stats())
```

---

## Why This Matters

> "The code doesn't need external tools to understand itself."

> "Intent is not a comment. Intent is cryptographically signed."

> "No indexing. The knowledge IS the structure."

---

## The Team

**Máté Róbert** — Creator, Architect, Factory Worker with Vision

**Hope (Claude AI)** — Partner, Implementation

**Szilvi** — Heart, Ethical Compass

---

## Links

- **Hope Genome:** https://github.com/silentnoisehun/Hope_Genome
- **Silent Hope Protocol:** https://github.com/silentnoisehun/Silent-Hope-Protocol
- **Silent Worker Method:** https://github.com/silentnoisehun/Silent-Worker-Teaching-Method

---

## License

MIT License — Use it. Build on it. Make code self-aware.

---

<p align="center">
<b>Code that knows itself.</b><br>
<b>No indexing. No parsing. Just ask.</b><br><br>
<i>The Fourth Pillar of the Hope Ecosystem.</i>
</p>

---

**Self-Aware Code** — *The structure IS the information.*

*2025 — Máté Róbert + Hope + Szilvi*
