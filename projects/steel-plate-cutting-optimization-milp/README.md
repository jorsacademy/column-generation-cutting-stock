# Steel Plate Cutting Optimization with MILP

A Python implementation of a two-dimensional steel plate cutting optimization problem using explicit geometric pattern generation and mixed-integer linear programming (MILP).

The model selects whole steel plates, satisfies customer demand, respects stock availability, and minimizes the combined cost of plates, cutting operations, and material waste.

## Features

- Integer decision variables through `scipy.optimize.milp`
- Explicit non-overlapping 2D placement for every accepted cutting pattern
- 90-degree piece rotation
- Multiple stock plate sizes and availability limits
- Demand satisfaction with `production >= demand`
- Plate cost, cutting cost, and waste penalty in the objective function
- Visualization of selected cutting-pattern geometry
- HiGHS MILP solver through SciPy

## Model structure

For each feasible cutting pattern `p`:

- `x[p]` = number of times cutting pattern `p` is used

Objective:

```text
minimize sum(pattern_cost[p] * x[p])
```

Demand constraints:

```text
sum(piece_count[i,p] * x[p]) >= demand[i]
```

Stock constraints:

```text
sum(x[p] for patterns using plate type k) <= available[k]
```

All `x[p]` variables are non-negative integers.

## Cutting-pattern generation

Candidate cutting patterns are generated for:

- single-piece-type patterns
- two-piece-type mixed patterns

Each candidate is validated using explicit orthogonal rectangle placement. A deterministic MaxRects-style packing heuristic is evaluated with multiple item orderings and both permitted orientations.

Every accepted pattern therefore includes a concrete, non-overlapping placement on its assigned stock plate.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

## Run

```bash
python steel_plate_cutting_optimizer.py
```

The program reports:

- number of feasible generated patterns
- optimal objective value
- selected cutting patterns and integer usage counts
- plate utilization percentages
- demand-versus-production verification
- total number of plates used

It also displays a Matplotlib visualization of the geometry for the most-used selected cutting pattern.

## Example instance

The included sample instance contains three stock plate types and five customer piece types with different dimensions and demand quantities.

For the supplied data, the implementation generates 689 feasible cutting patterns and HiGHS returns an optimal MILP solution using 17 plates.

The solution depends on the plate inventory, piece dimensions, demand values, and cost parameters defined in the script.

## Dependencies

- NumPy
- SciPy
- Matplotlib

SciPy provides the `milp` interface backed by the HiGHS optimization solver.

## Scope

This project demonstrates the integration of two-dimensional cutting-pattern generation with integer optimization for a steel cutting-stock problem.

Possible extensions include:

- kerf width
- guillotine-cut constraints
- grain direction
- trim margins
- plate defects
- remnant reuse
- machine-specific cutting sequences
- larger mixed-pattern search spaces
- exact or advanced industrial nesting algorithms
