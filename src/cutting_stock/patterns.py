from __future__ import annotations

from collections.abc import Iterable

from .data import CuttingStockInstance

Pattern = tuple[int, ...]


def used_length(instance: CuttingStockInstance, pattern: Pattern) -> int:
    validate_pattern(instance, pattern)
    return sum(count * length for count, length in zip(pattern, instance.item_lengths))


def waste(instance: CuttingStockInstance, pattern: Pattern) -> int:
    return instance.stock_length - used_length(instance, pattern)


def validate_pattern(instance: CuttingStockInstance, pattern: Pattern) -> None:
    if len(pattern) != instance.n_items:
        raise ValueError("pattern dimension does not match instance")
    if any(not isinstance(count, int) or count < 0 for count in pattern):
        raise ValueError("pattern counts must be nonnegative integers")
    if not any(pattern):
        raise ValueError("the zero pattern is not a cutting pattern")
    length = sum(count * item_length for count, item_length in zip(pattern, instance.item_lengths))
    if length > instance.stock_length:
        raise ValueError("pattern exceeds stock length")


def initial_patterns(instance: CuttingStockInstance) -> list[Pattern]:
    """Create one maximal single-item pattern for each demanded item type."""
    patterns: list[Pattern] = []
    for i, (length, demand) in enumerate(zip(instance.item_lengths, instance.demands)):
        if demand == 0:
            continue
        counts = [0] * instance.n_items
        counts[i] = instance.stock_length // length
        patterns.append(tuple(counts))
    return patterns


def enumerate_patterns(instance: CuttingStockInstance) -> list[Pattern]:
    """Enumerate all nonzero feasible patterns; intended only for small benchmarks."""
    result: list[Pattern] = []
    current = [0] * instance.n_items

    def recurse(index: int, remaining: int) -> None:
        if index == instance.n_items:
            if any(current):
                result.append(tuple(current))
            return
        length = instance.item_lengths[index]
        for count in range(remaining // length + 1):
            current[index] = count
            recurse(index + 1, remaining - count * length)
        current[index] = 0

    recurse(0, instance.stock_length)
    return result


def pattern_matrix(patterns: Iterable[Pattern], n_items: int):
    import numpy as np

    materialized = list(patterns)
    if not materialized:
        raise ValueError("at least one pattern is required")
    matrix = np.asarray(materialized, dtype=float).T
    if matrix.shape[0] != n_items:
        raise ValueError("pattern dimension mismatch")
    return matrix
