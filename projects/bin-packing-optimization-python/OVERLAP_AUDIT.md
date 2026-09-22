# Repository Overlap Audit — Packing and Cutting

This document records portfolio overlap without changing repository ownership, history, visibility, or project boundaries.

## Status legend

- **Keep separate** — materially different mathematical problem, method, or experimental objective.
- **Overlap but justified** — substantial shared content, but the educational/research role differs enough to justify a separate repository.
- **Potential consolidation** — unusually high duplication; review again before any future merge or archival action.

## High-overlap pair

### `bin-packing-optimization-python`

Role: foundational one-dimensional bin-packing project.

Distinctive scope:

- exact PuLP/CBC MILP;
- First Fit Decreasing heuristic;
- explicit exact-vs-heuristic comparison;
- tests for optimum, feasibility, capacity, item identity, and invalid input.

### `bin-packing-milp-pulp-visualization`

Role: compact PuLP MILP demonstration with a stronger visualization emphasis.

Distinctive scope:

- exact MILP formulation;
- bin-utilization reporting;
- theoretical lower bound;
- random-instance generation;
- Matplotlib packing visualization.

### Audit decision

**Potential consolidation — but no action now.**

The mathematical core is substantially the same one-dimensional bin-packing MILP. The first repository has the stronger methodological comparison because it includes FFD and tests; the second has the clearer visualization/demo layer. If portfolio reduction is ever desired, the visualization features could be moved into `bin-packing-optimization-python` and the second repository could then be archived rather than deleted.

Until that decision is made, both repositories remain unchanged.

## Related repositories that should stay separate

- `miter-aware-cutting-stock-milp` — cutting stock with geometry/application-specific constraints; not the same problem as identical-bin packing.
- `column-generation-cutting-stock` — decomposition/column-generation methodology; computationally distinct from compact MILP bin packing.
- `steel-plate-cutting-optimization-milp` — plate-cutting application with different geometry and decision structure.
- `freighter-container-loading-optimization` — loading/packing application with different physical constraints.
- `warehouse-order-packing-heuristics` — heuristic operational packing rather than the same exact MILP benchmark.

## Portfolio rule

Do not consolidate repositories merely because they contain the words `packing`, `cutting`, or `loading`. Consolidation is justified only when both the optimization model and the computational experiment are substantially duplicated.
