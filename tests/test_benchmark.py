"""Tests for benchmark suite."""

from benchmarks.benchmark import (
    benchmark_ask_queries,
    benchmark_crypto,
    benchmark_decorator_overhead,
)


def test_benchmark_functions_execute():
    """Verify that benchmark functions run without error."""
    elapsed, per_func_us = benchmark_decorator_overhead(iterations=10)
    assert elapsed > 0
    assert per_func_us > 0

    crypto_results = benchmark_crypto(iterations=10)
    assert "hash_us" in crypto_results
    assert "keygen_ms" in crypto_results

    avg_us = benchmark_ask_queries(num_queries=5)
    assert avg_us >= 0
