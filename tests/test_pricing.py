import numpy as np
import pytest

from cutting_stock.data import CuttingStockInstance
from cutting_stock.patterns import enumerate_patterns
from cutting_stock.pricing import solve_pricing


def test_pricing_matches_brute_force_pattern_enumeration():
    instance = CuttingStockInstance(10, (3, 4, 6), (2, 2, 1))
    dual = np.array([0.31, 0.48, 0.71])
    result = solve_pricing(instance, dual)
    patterns = enumerate_patterns(instance)
    brute_value = max(sum(a * y for a, y in zip(pattern, dual)) for pattern in patterns)
    assert result.dual_value == pytest.approx(brute_value)
    assert result.reduced_cost == pytest.approx(1.0 - brute_value)


def test_known_pricing_pattern():
    instance = CuttingStockInstance(10, (4, 6), (1, 1))
    result = solve_pricing(instance, np.array([0.6, 0.7]))
    assert result.pattern == (1, 1)
    assert result.dual_value == pytest.approx(1.3)
