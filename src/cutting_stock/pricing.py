from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .data import CuttingStockInstance
from .patterns import Pattern


@dataclass(frozen=True)
class PricingResult:
    pattern: Pattern
    dual_value: float
    reduced_cost: float


def solve_pricing(instance: CuttingStockInstance, dual_prices: np.ndarray) -> PricingResult:
    """Solve the unbounded integer-knapsack pricing problem by dynamic programming."""
    dual = np.asarray(dual_prices, dtype=float)
    if dual.shape != (instance.n_items,):
        raise ValueError("dual_prices has incorrect dimension")
    if np.any(~np.isfinite(dual)):
        raise ValueError("dual_prices must be finite")

    length_limit = instance.stock_length
    values = [0.0] * (length_limit + 1)
    patterns: list[Pattern] = [(0,) * instance.n_items for _ in range(length_limit + 1)]

    for capacity in range(1, length_limit + 1):
        best_value = values[capacity - 1]
        best_pattern = patterns[capacity - 1]
        for i, item_length in enumerate(instance.item_lengths):
            if item_length > capacity:
                continue
            candidate_value = values[capacity - item_length] + dual[i]
            if candidate_value > best_value + 1e-12:
                counts = list(patterns[capacity - item_length])
                counts[i] += 1
                best_value = candidate_value
                best_pattern = tuple(counts)
        values[capacity] = best_value
        patterns[capacity] = best_pattern

    pattern = patterns[length_limit]
    return PricingResult(
        pattern=pattern,
        dual_value=float(values[length_limit]),
        reduced_cost=float(1.0 - values[length_limit]),
    )
