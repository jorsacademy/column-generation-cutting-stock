# Bin Packing MILP with PuLP and Visualization

This project solves the one-dimensional **Bin Packing Problem** exactly using **Mixed-Integer Linear Programming (MILP)** with **PuLP** and the CBC solver. It also includes a Matplotlib visualization of the resulting packing plan.

## Problem

Given a set of items with known weights and identical bins with fixed capacity, assign every item to exactly one bin while minimizing the total number of bins used.

## MILP formulation

Binary decision variables:

- `x[i,j] = 1` if item `i` is assigned to bin `j`.
- `y[j] = 1` if bin `j` is used.

Objective:

```text
minimize  sum_j y[j]
```

Subject to:

```text
sum_j x[i,j] = 1                         for every item i
sum_i weight[i] * x[i,j] <= C * y[j]    for every bin j
```

where `C` is the bin capacity.

The implementation also adds a symmetry-breaking constraint so candidate bins are activated in order. This reduces equivalent solutions and can improve solution time.

## Features

- Exact MILP solution with PuLP/CBC
- Input validation for infeasible or invalid instances
- Optional upper bound on the number of candidate bins
- Solver status and runtime reporting
- Human-readable allocation output
- Bin utilization percentages
- Theoretical lower-bound reporting
- Matplotlib packing visualization
- Reproducible random instance generation via `seed`

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python bin_packing.py
```

The script first solves a predefined example and then a larger random instance.

## Example

```python
from bin_packing import solve_bin_packing, print_solution, visualize_solution

weights = [4, 8, 1, 4, 2, 1, 7, 3, 5, 2]
bin_capacity = 10

status, bins_used, allocation = solve_bin_packing(weights, bin_capacity)
print_solution(weights, bin_capacity, bins_used, allocation)
visualize_solution(weights, bin_capacity, allocation)
```

## Project structure

```text
.
├── bin_packing.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Notes

Bin Packing is NP-hard. MILP provides an exact solution, but runtime can increase substantially as the number of items grows. For large-scale instances, heuristics or metaheuristics such as First Fit Decreasing, Best Fit Decreasing, Genetic Algorithms, Simulated Annealing, or Variable Neighborhood Search may be more practical.

## License

No license file is included by default. Add a license if you intend to define explicit reuse terms.
