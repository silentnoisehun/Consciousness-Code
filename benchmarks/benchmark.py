"""
Consciousness Code - Benchmark Suite

Measures actual runtime performance, memory footprint,
query response latency, decorator overhead, and cryptographic operations.
"""

import gc
import os
import sys
import time

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from consciousness_code import (
    ask,
    aware,
    generate_author_key,
    hash_code,
    memory,
    sign_block,
    verify_block,
)
from consciousness_code.core import CodeBlock


def benchmark_decorator_overhead(iterations: int = 1000):
    """Measure the overhead of applying @aware decorator."""
    start = time.perf_counter()
    for i in range(iterations):
        @aware(
            intent=f"Benchmark function {i}",
            author="benchmarker",
            tags=[f"tag_{i % 10}", "benchmark"],
        )
        def sample_func():
            return i
    elapsed = time.perf_counter() - start
    per_func_us = (elapsed / iterations) * 1_000_000
    print(f"[Decorator Overhead] {iterations} functions registered in {elapsed:.4f}s ({per_func_us:.2f} μs/func)")
    return elapsed, per_func_us


def benchmark_memory_footprint(num_blocks: int = 10000):
    """Measure approximate memory footprint per registered CodeBlock."""
    mem = memory()

    gc.collect()
    start_time = time.perf_counter()

    for i in range(num_blocks):
        b = CodeBlock(
            name=f"bench_fn_{i}",
            qualified_name=f"bench_module.bench_fn_{i}",
            hash="a" * 64,
            author="bench_author",
            intent=f"Intent for function {i}",
            description=f"Description for function {i}",
            tags={f"tag_{i % 50}", "benchmark_block"},
        )
        mem.register(b)

    elapsed = time.perf_counter() - start_time
    total_blocks = len(mem.all())

    print(f"[Memory Scale] Memory population of {num_blocks} blocks took {elapsed:.4f}s (Total blocks: {total_blocks})")
    return total_blocks, elapsed


def benchmark_ask_queries(num_queries: int = 100):
    """Measure query execution latency with ask()."""
    queries = ["intent", "bench_author", "tag_5", "nonexistent_query", "function 500"]

    start = time.perf_counter()
    total_results = 0
    for _ in range(num_queries):
        for q in queries:
            res = ask(q)
            total_results += len(res)

    elapsed = time.perf_counter() - start
    avg_us_per_query = (elapsed / (num_queries * len(queries))) * 1_000_000

    print(f"[Query Latency] {num_queries * len(queries)} queries executed across {len(memory().all())} blocks in {elapsed:.4f}s ({avg_us_per_query:.2f} μs/query)")
    return avg_us_per_query


def benchmark_crypto(iterations: int = 100):
    """Measure Ed25519 key generation, hashing, signing, and verification speeds."""
    # 1. Hashing
    sample_code = "def compute_data(x, y):\n    return x * y + 42\n" * 10
    start = time.perf_counter()
    for _ in range(1000):
        _ = hash_code(sample_code)
    hash_elapsed = time.perf_counter() - start
    hash_us = (hash_elapsed / 1000) * 1_000_000

    # 2. Key Generation
    start = time.perf_counter()
    keys = [generate_author_key() for _ in range(iterations)]
    keygen_elapsed = time.perf_counter() - start
    keygen_ms = (keygen_elapsed / iterations) * 1000

    # 3. Signing
    code_hash = hash_code(sample_code)
    intent = "Authenticate user and authorize access"
    start = time.perf_counter()
    signatures = []
    for i in range(iterations):
        sig = sign_block(keys[i].private_key, code_hash, intent)
        signatures.append(sig)
    sign_elapsed = time.perf_counter() - start
    sign_ms = (sign_elapsed / iterations) * 1000

    # 4. Verification
    start = time.perf_counter()
    for i in range(iterations):
        valid = verify_block(keys[i].public_key, signatures[i], code_hash, intent)
        assert valid
    verify_elapsed = time.perf_counter() - start
    verify_ms = (verify_elapsed / iterations) * 1000

    print(f"[Crypto] SHA3-256 Hashing: {hash_us:.2f} μs/op ({1_000_000/hash_us:.0f} ops/sec)")
    print(f"[Crypto] Author Key Gen:   {keygen_ms:.2f} ms/key ({1000/keygen_ms:.0f} keys/sec)")
    print(f"[Crypto] Ed25519 Signing:  {sign_ms:.2f} ms/sig ({1000/sign_ms:.0f} sigs/sec)")
    print(f"[Crypto] Ed25519 Verify:   {verify_ms:.2f} ms/verify ({1000/verify_ms:.0f} verifications/sec)")

    return {
        "hash_us": hash_us,
        "keygen_ms": keygen_ms,
        "sign_ms": sign_ms,
        "verify_ms": verify_ms,
    }


def run_all_benchmarks():
    print("============================================================")
    print("         CONSCIOUSNESS CODE BENCHMARK RESULTS               ")
    print("============================================================")
    print(f"Python Version: {sys.version.split()[0]}")
    print()

    dec_elapsed, dec_us = benchmark_decorator_overhead(1000)
    total_blocks, pop_elapsed = benchmark_memory_footprint(10000)
    ask_latency_us = benchmark_ask_queries(100)
    crypto_res = benchmark_crypto(100)

    print("\n============================================================")
    print("SUMMARY")
    print("============================================================")
    print(f"Decorator Registration: {dec_us:.2f} μs / function")
    print(f"Memory Search Query:    {ask_latency_us:.2f} μs / query (over 10,000+ blocks)")
    print(f"Code Hashing:           {crypto_res['hash_us']:.2f} μs / hash")
    print(f"Key Generation:         {crypto_res['keygen_ms']:.2f} ms / key")
    print(f"Ed25519 Signing:        {crypto_res['sign_ms']:.2f} ms / signature")
    print(f"Ed25519 Verification:   {crypto_res['verify_ms']:.2f} ms / verification")
    print("============================================================")


if __name__ == "__main__":
    run_all_benchmarks()
