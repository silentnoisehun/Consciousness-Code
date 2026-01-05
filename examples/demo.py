"""
Consciousness Code Demo

This example shows how code can know itself.
No indexing. No parsing. Just ask.
"""

from consciousness_code import aware, aware_class, ask, explain, memory, stats


# =============================================================================
# Make functions self-aware
# =============================================================================

@aware(
    intent="Main entry point for the application",
    author="mate",
    tags=["main", "entry"]
)
def main():
    """Application entry point."""
    print("Starting application...")
    result = process_data({"name": "test"})
    generate_report(result)
    print("Done!")


@aware(
    intent="Process incoming data and validate",
    author="mate",
    tags=["data", "processing", "validation"]
)
def process_data(data: dict) -> dict:
    """Process and validate incoming data."""
    if not data:
        raise ValueError("Empty data")
    return {"processed": True, **data}


@aware(
    intent="Generate final report from processed data",
    author="mate",
    tags=["report", "output", "generation"]
)
def generate_report(data: dict) -> str:
    """Generate a report from processed data."""
    return f"Report: {data}"


@aware(
    intent="Authenticate users securely",
    author="hope",
    tags=["auth", "security", "login"]
)
def authenticate(username: str, password: str) -> bool:
    """Authenticate a user."""
    # Demo implementation
    return username == "admin" and password == "secret"


@aware_class(
    intent="Handle database connections",
    author="mate",
    tags=["database", "connection", "storage"]
)
class DatabaseConnection:
    """Database connection handler."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def connect(self):
        """Connect to database."""
        print(f"Connecting to {self.connection_string}")

    def query(self, sql: str):
        """Execute a query."""
        print(f"Executing: {sql}")


# =============================================================================
# Now ASK the code!
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CONSCIOUSNESS CODE DEMO")
    print("=" * 60)
    print()

    # Ask about data processing
    print("Q: What handles data?")
    print("-" * 40)
    for code in ask("data"):
        print(f"  {code.name}: {code.intent}")
    print()

    # Ask about security
    print("Q: What handles security?")
    print("-" * 40)
    for code in ask("security"):
        print(f"  {code.name}: {code.intent}")
    print()

    # Ask a function to explain itself
    print("Q: Explain the main function")
    print("-" * 40)
    print(main.__aware__.explain())
    print()

    # Ask who wrote what
    print("Q: Who wrote what?")
    print("-" * 40)
    for block in memory().all():
        print(f"  {block.name}: written by {block.author}")
    print()

    # Get stats
    print("Memory Statistics:")
    print("-" * 40)
    for key, value in stats().items():
        print(f"  {key}: {value}")
    print()

    print("=" * 60)
    print("The code knows itself. No indexing required.")
    print("=" * 60)
