# Packing, Cutting, and Loading Research Series

This file maps repositories built around packing, cutting, loading, and pattern-generation problems. It is an index only: the projects remain independent because one-dimensional packing, cutting-stock column generation, geometric cutting, and container loading are materially different optimization problems.

## Bin packing

- `bin-packing-optimization-python` — one-dimensional bin packing with an exact MILP model plus First Fit Decreasing for method comparison.
- `bin-packing-milp-pulp-visualization` — compact exact PuLP formulation with visualization and utilization reporting.

These two are intentionally close, but they serve different educational purposes: one emphasizes exact-vs-heuristic comparison and tests, while the other emphasizes a compact visual MILP demonstration.

## Cutting stock and material cutting

- `column-generation-cutting-stock` — cutting stock through restricted-master/pricing decomposition.
- `miter-aware-cutting-stock-milp` — cutting-stock formulation with miter-aware constraints.
- `steel-plate-cutting-optimization-milp` — plate-cutting application with a different geometric/material context.

## Loading and packing applications

- `freighter-container-loading-optimization` — freight/container loading.
- `warehouse-order-packing-heuristics` — warehouse packing heuristics rather than an exact packing model.

## Why these stay separate

The shared vocabulary of "packing" hides different mathematical structures:

- one-dimensional bin packing;
- cutting stock with pattern generation;
- geometric/material cutting;
- container loading;
- heuristic warehouse packing.

A single monorepo would blur these distinctions. The useful organization is a comparative series, not consolidation.
