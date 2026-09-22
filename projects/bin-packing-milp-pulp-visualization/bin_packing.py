from __future__ import annotations

import random
from math import ceil
from time import perf_counter
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pulp


Allocation = Dict[int, List[int]]


def _validate_inputs(weights: List[float], bin_capacity: float, max_bins: Optional[int]) -> int:
    """Validate the bin-packing instance and return the effective bin limit."""
    if not weights:
        raise ValueError("weights must contain at least one item.")
    if bin_capacity <= 0:
        raise ValueError("bin_capacity must be positive.")
    if any(weight <= 0 for weight in weights):
        raise ValueError("All item weights must be positive.")
    if any(weight > bin_capacity for weight in weights):
        raise ValueError("Every item must fit into an empty bin.")

    n = len(weights)
    effective_max_bins = n if max_bins is None else max_bins

    if effective_max_bins <= 0:
        raise ValueError("max_bins must be positive.")
    if effective_max_bins > n:
        effective_max_bins = n

    theoretical_minimum = ceil(sum(weights) / bin_capacity)
    if effective_max_bins < theoretical_minimum:
        raise ValueError(
            f"max_bins={effective_max_bins} is smaller than the theoretical minimum "
            f"of {theoretical_minimum}."
        )

    return effective_max_bins


def solve_bin_packing(
    weights: List[float],
    bin_capacity: float,
    max_bins: Optional[int] = None,
) -> Tuple[int, int, Allocation]:
    """Solve the one-dimensional bin packing problem using MILP and PuLP.

    Parameters
    ----------
    weights:
        Positive item weights.
    bin_capacity:
        Capacity of each identical bin.
    max_bins:
        Optional upper bound on the number of candidate bins.

    Returns
    -------
    tuple
        ``(status, bins_used, allocation)`` where ``status`` is the PuLP status
        code and ``allocation`` maps each used bin index to item indices.
    """
    max_bins = _validate_inputs(weights, bin_capacity, max_bins)
    n = len(weights)

    problem = pulp.LpProblem("Bin_Packing_Problem", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "item_assignment",
        [(i, j) for i in range(n) for j in range(max_bins)],
        cat=pulp.LpBinary,
    )
    y = pulp.LpVariable.dicts(
        "bin_used",
        range(max_bins),
        cat=pulp.LpBinary,
    )

    problem += pulp.lpSum(y[j] for j in range(max_bins)), "MinimizeBins"

    for i in range(n):
        problem += (
            pulp.lpSum(x[(i, j)] for j in range(max_bins)) == 1,
            f"AssignItem_{i}",
        )

    for j in range(max_bins):
        problem += (
            pulp.lpSum(weights[i] * x[(i, j)] for i in range(n))
            <= bin_capacity * y[j],
            f"CapacityBin_{j}",
        )

    # Symmetry breaking: used bins are activated from left to right.
    for j in range(1, max_bins):
        problem += y[j] <= y[j - 1], f"OrderedBins_{j}"

    start_time = perf_counter()
    status = problem.solve(pulp.PULP_CBC_CMD(msg=False))
    solve_time = perf_counter() - start_time

    status_name = pulp.LpStatus[status]
    print(f"Solution status: {status_name}")
    print(f"Solution time: {solve_time:.4f} seconds")

    if status_name != "Optimal":
        return status, 0, {}

    objective_value = pulp.value(problem.objective)
    if objective_value is None:
        raise RuntimeError("Solver returned no objective value despite optimal status.")

    allocation: Allocation = {}
    for j in range(max_bins):
        y_value = pulp.value(y[j])
        if y_value is not None and y_value > 0.5:
            allocation[j] = [
                i
                for i in range(n)
                if (pulp.value(x[(i, j)]) or 0.0) > 0.5
            ]

    return status, int(round(objective_value)), allocation


def print_solution(
    weights: List[float],
    bin_capacity: float,
    bins_used: int,
    allocation: Allocation,
) -> None:
    """Print the bin-packing solution in a readable format."""
    print("\nBin Packing Solution Summary:")
    print(f"Number of items: {len(weights)}")
    print(f"Bin capacity: {bin_capacity}")
    print(f"Number of bins used: {bins_used}")

    if not allocation:
        print("No feasible allocation is available.")
        return

    print("\nDetailed Allocation:")
    total_weight = 0.0

    for display_bin, bin_idx in enumerate(sorted(allocation), start=1):
        items = allocation[bin_idx]
        bin_weight = sum(weights[i] for i in items)
        total_weight += bin_weight
        utilization = bin_weight / bin_capacity * 100

        print(
            f"Bin {display_bin}: Weight {bin_weight}/{bin_capacity} "
            f"({utilization:.1f}% full)"
        )
        print(
            f"  Items: {[i + 1 for i in items]} "
            f"with weights {[weights[i] for i in items]}"
        )

    print(f"\nTotal weight of all items: {total_weight}")
    print(f"Theoretical minimum bins: {ceil(total_weight / bin_capacity)}")


def visualize_solution(
    weights: List[float],
    bin_capacity: float,
    allocation: Allocation,
) -> None:
    """Visualize each used bin as a stacked collection of packed items."""
    if not allocation:
        print("No allocation to visualize.")
        return

    used_bins = sorted(allocation)
    display_positions = {bin_idx: pos for pos, bin_idx in enumerate(used_bins)}

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(weights)))

    for bin_idx in used_bins:
        x_pos = display_positions[bin_idx]
        ax.add_patch(
            plt.Rectangle(
                (x_pos, 0),
                0.8,
                bin_capacity,
                fill=False,
                edgecolor="black",
            )
        )

        current_height = 0.0
        for item_idx in allocation[bin_idx]:
            item_weight = weights[item_idx]
            ax.add_patch(
                plt.Rectangle(
                    (x_pos, current_height),
                    0.8,
                    item_weight,
                    facecolor=colors[item_idx],
                    edgecolor="black",
                    alpha=0.7,
                )
            )
            ax.text(
                x_pos + 0.4,
                current_height + item_weight / 2,
                f"{item_idx + 1}\n({item_weight})",
                ha="center",
                va="center",
            )
            current_height += item_weight

    n_used = len(used_bins)
    ax.set_xlim(-0.5, n_used + 0.3)
    ax.set_ylim(0, bin_capacity * 1.1)
    ax.set_xlabel("Bin Number")
    ax.set_ylabel("Weight / Capacity")
    ax.set_title("Bin Packing Solution Visualization")
    ax.set_xticks(range(n_used))
    ax.set_xticklabels([f"Bin {i + 1}" for i in range(n_used)])

    plt.tight_layout()
    plt.show()


def generate_random_instance(
    n_items: int,
    weight_range: Tuple[int, int] = (1, 10),
    bin_capacity: Optional[int] = None,
    seed: Optional[int] = None,
) -> Tuple[List[int], int]:
    """Generate a reproducible random bin-packing instance."""
    if n_items <= 0:
        raise ValueError("n_items must be positive.")
    if weight_range[0] <= 0 or weight_range[0] > weight_range[1]:
        raise ValueError("weight_range must contain positive values in ascending order.")

    rng = random.Random(seed)
    weights = [rng.randint(weight_range[0], weight_range[1]) for _ in range(n_items)]

    if bin_capacity is None:
        bin_capacity = max(max(weights), int(sum(weights) / (n_items / 3)))

    if bin_capacity <= 0:
        raise ValueError("bin_capacity must be positive.")
    if any(weight > bin_capacity for weight in weights):
        raise ValueError("Generated item weights must not exceed bin_capacity.")

    return weights, bin_capacity


if __name__ == "__main__":
    weights = [4, 8, 1, 4, 2, 1, 7, 3, 5, 2]
    bin_capacity = 10

    print("Solving predefined bin packing problem...")
    status, bins_used, allocation = solve_bin_packing(weights, bin_capacity)
    print_solution(weights, bin_capacity, bins_used, allocation)
    visualize_solution(weights, bin_capacity, allocation)

    print("\n" + "=" * 60)
    print("Solving a larger random instance...")

    weights, bin_capacity = generate_random_instance(
        25,
        weight_range=(5, 30),
        bin_capacity=50,
        seed=42,
    )

    status, bins_used, allocation = solve_bin_packing(weights, bin_capacity)
    print_solution(weights, bin_capacity, bins_used, allocation)
    visualize_solution(weights, bin_capacity, allocation)
