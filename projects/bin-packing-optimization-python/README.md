# Bin Packing Optimization in Python

A medium-level implementation of the one-dimensional Bin Packing Problem in Python.

The project contains two solution approaches:

- an exact Mixed-Integer Linear Programming (MILP) model implemented with PuLP;
- a First Fit Decreasing (FFD) heuristic for comparison.

The exact model minimizes the number of identical bins required to pack all items while ensuring that the total weight assigned to each bin does not exceed its capacity.

## Problem Statement

A logistics company needs to pack a set of items into identical shipping bins. Each item has a known weight, and each bin has the same maximum capacity. Every item must be assigned to exactly one bin.

For the example instance used in this repository:

- number of items: 18;
- item weights: `[9, 8, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 7, 1, 8, 4, 6]`;
- bin capacity: `15`.

The objective is to minimize the total number of bins used.

## Mathematical Model

Let:

- `i` denote an item;
- `j` denote a candidate bin;
- `w[i]` be the weight of item `i`;
- `C` be the bin capacity;
- `x[i,j] = 1` if item `i` is assigned to bin `j`, otherwise `0`;
- `y[j] = 1` if bin `j` is used, otherwise `0`.

Objective:

```text
minimize  sum_j y[j]
```

Subject to:

```text
sum_j x[i,j] = 1                         for every item i
sum_i w[i] * x[i,j] <= C * y[j]          for every bin j
x[i,j] in {0,1}
y[j] in {0,1}
```

The implementation also adds a simple symmetry-breaking condition so candidate bins are activated in order. This does not change the feasible packing decisions; it reduces equivalent solutions caused by interchangeable bin labels.

## Project Structure

```text
bin-packing-optimization-python/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── src/
│   ├── bin_packing.py
│   └── heuristic.py
└── tests/
    └── test_bin_packing.py
```

## Installation

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Activate the environment and install the dependencies:

```bash
pip install -r requirements.txt
```

## Run the Exact Optimization Model

```bash
python src/bin_packing.py
```

The program prints the solver status, minimum number of bins, item IDs assigned to each bin, bin loads, and remaining capacity.

Item IDs are kept separate from item weights. This is important because sorting a plain list of weights can destroy the relationship between an item and its original identifier.

## Run the Tests

```bash
pytest
```

The tests check that:

- the exact model obtains the expected optimum for a small instance;
- all items are assigned exactly once;
- no bin exceeds capacity;
- the FFD heuristic preserves original item identifiers;
- invalid instances are rejected.

## Exact Optimization vs. FFD

The MILP model is an exact optimization method. When the solver reports an optimal solution, the number of bins is mathematically optimal for the supplied instance.

First Fit Decreasing is a heuristic. It is typically fast and often produces good packings, but it does not guarantee the minimum number of bins for every instance. It is included to demonstrate the distinction between optimization and heuristic solution methods.

## License

This repository uses a custom non-commercial license. Personal, educational, academic, and non-commercial research use is permitted under the terms in `LICENSE`.

Commercial use, commercial redistribution, incorporation into a commercial product or service, and other revenue-generating use require prior written permission from the copyright holder.

This custom license is intentionally not an OSI-approved open-source license because it restricts commercial use.
