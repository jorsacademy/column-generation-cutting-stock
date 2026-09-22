"""Exact Bin Packing model solved with Mixed-Integer Linear Programming.

This module builds and solves a one-dimensional Bin Packing Problem using PuLP.
The objective is to minimize the number of identical bins required to pack all
items without exceeding the capacity of any used bin.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pulp


@dataclass(frozen=True)
class BinPackingInstance:
    """Input data for a Bin Packing instance."""

    weights: List[int]
    capacity: int

    def validate(self) -> None:
        """Validate that the instance is feasible and well-defined."""
        if not self.weights:
            raise ValueError("At least one item is required.")
        if self.capacity <= 0:
            raise ValueError("Bin capacity must be positive.")
        if any(weight <= 0 for weight in self.weights):
            raise ValueError("All item weights must be positive.")
        if any(weight > self.capacity for weight in self.weights):
            raise ValueError("Every item must fit into an empty bin.")


@dataclass
class BinPackingSolution:
    """Solved Bin Packing result."""

    bins: Dict[int, List[int]]
    bin_loads: Dict[int, int]
    objective_value: int
    status: str


def solve_bin_packing(instance: BinPackingInstance) -> BinPackingSolution:
    """Solve the Bin Packing Problem exactly with a MILP model.

    Decision variables
    ------------------
    x[i, j] = 1 if item i is assigned to bin j, otherwise 0.
    y[j] = 1 if bin j is used, otherwise 0.

    The number of candidate bins is bounded by the number of items. This is a
    standard safe upper bound because each item could be placed in its own bin.
    """
    instance.validate()

    weights = instance.weights
    capacity = instance.capacity
    items = range(len(weights))
    candidate_bins = range(len(weights))

    model = pulp.LpProblem("BinPacking", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "assign",
        ((i, j) for i in items for j in candidate_bins),
        cat=pulp.LpBinary,
    )
    y = pulp.LpVariable.dicts("use_bin", candidate_bins, cat=pulp.LpBinary)

    model += pulp.lpSum(y[j] for j in candidate_bins), "MinimizeNumberOfBins"

    for i in items:
        model += (
            pulp.lpSum(x[(i, j)] for j in candidate_bins) == 1,
            f"AssignItem_{i}",
        )

    for j in candidate_bins:
        model += (
            pulp.lpSum(weights[i] * x[(i, j)] for i in items)
            <= capacity * y[j],
            f"CapacityBin_{j}",
        )

    # Symmetry-breaking constraint: candidate bins are activated in order.
    for j in range(len(weights) - 1):
        model += y[j] >= y[j + 1], f"OrderedBins_{j}"

    solver = pulp.PULP_CBC_CMD(msg=False)
    model.solve(solver)

    status = pulp.LpStatus[model.status]
    if status != "Optimal":
        raise RuntimeError(f"The optimization model did not solve optimally: {status}")

    bins: Dict[int, List[int]] = {}
    bin_loads: Dict[int, int] = {}

    for j in candidate_bins:
        if pulp.value(y[j]) > 0.5:
            assigned_items = [i for i in items if pulp.value(x[(i, j)]) > 0.5]
            bins[j] = assigned_items
            bin_loads[j] = sum(weights[i] for i in assigned_items)

    objective_value = int(round(pulp.value(model.objective)))

    return BinPackingSolution(
        bins=bins,
        bin_loads=bin_loads,
        objective_value=objective_value,
        status=status,
    )


def print_solution(instance: BinPackingInstance, solution: BinPackingSolution) -> None:
    """Print a readable solution while preserving original item identifiers."""
    print(f"Solver status: {solution.status}")
    print(f"Minimum number of bins: {solution.objective_value}")

    for display_index, bin_id in enumerate(sorted(solution.bins), start=1):
        item_indices = solution.bins[bin_id]
        item_labels = [index + 1 for index in item_indices]
        item_weights = [instance.weights[index] for index in item_indices]
        load = solution.bin_loads[bin_id]
        remaining = instance.capacity - load

        print(
            f"Bin {display_index}: items={item_labels}, "
            f"weights={item_weights}, load={load}/{instance.capacity}, "
            f"remaining={remaining}"
        )


if __name__ == "__main__":
    example = BinPackingInstance(
        weights=[9, 8, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 7, 1, 8, 4, 6],
        capacity=15,
    )
    result = solve_bin_packing(example)
    print_solution(example, result)
