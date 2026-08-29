import pytest

from cutting_stock.data import CuttingStockInstance, demo_instance
from cutting_stock.patterns import enumerate_patterns, initial_patterns, used_length, validate_pattern


def test_instance_validation():
    with pytest.raises(ValueError):
        CuttingStockInstance(10, (3, 3), (1, 1))
    with pytest.raises(ValueError):
        CuttingStockInstance(10, (3, 11), (1, 1))
    with pytest.raises(ValueError):
        CuttingStockInstance(10, (3,), (0,))


def test_initial_patterns_are_feasible():
    instance = demo_instance()
    for pattern in initial_patterns(instance):
        validate_pattern(instance, pattern)
        assert used_length(instance, pattern) <= instance.stock_length


def test_enumeration_is_complete_for_tiny_instance():
    instance = CuttingStockInstance(5, (2, 3), (1, 1))
    patterns = set(enumerate_patterns(instance))
    assert patterns == {(1, 0), (2, 0), (0, 1), (1, 1)}
