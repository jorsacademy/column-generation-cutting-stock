"""First Fit Decreasing heuristic for the Bin Packing Problem.

The heuristic is included for comparison with the exact MILP solution. Unlike
sorting a bare list of weights, this implementation keeps each original item ID
attached to its weight so the final packing remains traceable.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def first_fit_decreasing(weights: List[int], capacity: int) -> Dict[int, List[int]]:
    """Pack items with the First Fit Decreasing heuristic.

    Parameters
    ----------
    weights:
        Positive item weights.
    capacity:
        Maximum capacity of each bin.

    Returns
    -------
    dict
        Mapping from bin ID to original zero-based item indices.
    """
    if not weights:
        raise ValueError("At least one item is required.")
    if capacity <= 0:
        raise ValueError("Bin capacity must be positive.")
    if any(weight <= 0 for weight in weights):
        raise ValueError("All item weights must be positive.")
    if any(weight > capacity for weight in weights):
        raise ValueError("Every item must fit into an empty bin.")

    indexed_items: List[Tuple[int, int]] = sorted(
        enumerate(weights), key=lambda pair: pair[1], reverse=True
    )

    bins: Dict[int, List[int]] = {}
    loads: Dict[int, int] = {}

    for item_id, weight in indexed_items:
        placed = False

        for bin_id in bins:
            if loads[bin_id] + weight <= capacity:
                bins[bin_id].append(item_id)
                loads[bin_id] += weight
                placed = True
                break

        if not placed:
            new_bin_id = len(bins)
            bins[new_bin_id] = [item_id]
            loads[new_bin_id] = weight

    return bins
