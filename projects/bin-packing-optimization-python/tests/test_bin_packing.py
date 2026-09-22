"""Tests for the Bin Packing implementations."""

import pytest

from src.bin_packing import BinPackingInstance, solve_bin_packing
from src.heuristic import first_fit_decreasing


def test_exact_solver_returns_feasible_optimum() -> None:
    instance = BinPackingInstance(weights=[8, 7, 6, 5, 4], capacity=10)
    solution = solve_bin_packing(instance)

    assert solution.status == "Optimal"
    assert solution.objective_value == 4

    assigned_items = [item for items in solution.bins.values() for item in items]
    assert sorted(assigned_items) == list(range(len(instance.weights)))

    for load in solution.bin_loads.values():
        assert load <= instance.capacity


def test_ffd_preserves_original_item_ids() -> None:
    weights = [5, 9, 4, 6]
    bins = first_fit_decreasing(weights, capacity=10)

    assigned_items = [item for items in bins.values() for item in items]
    assert sorted(assigned_items) == list(range(len(weights)))

    for items in bins.values():
        assert sum(weights[item] for item in items) <= 10


def test_invalid_instance_rejects_oversized_item() -> None:
    instance = BinPackingInstance(weights=[4, 11], capacity=10)

    with pytest.raises(ValueError, match="Every item must fit"):
        solve_bin_packing(instance)
