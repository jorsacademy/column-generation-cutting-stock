from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

from .data import CuttingStockInstance
from .patterns import Pattern, pattern_matrix


@dataclass(frozen=True)
class MasterLPSolution:
    objective: float
    usage: np.ndarray
    dual_prices: np.ndarray
    message: str


@dataclass(frozen=True)
class IntegerMasterSolution:
    objective: float
    usage: np.ndarray
    message: str


def solve_master_lp(instance: CuttingStockInstance, patterns: list[Pattern]) -> MasterLPSolution:
    """Solve the restricted LP master and return nonnegative demand dual prices."""
    A = pattern_matrix(patterns, instance.n_items)
    demands = np.asarray(instance.demands, dtype=float)
    result = linprog(
        c=np.ones(len(patterns), dtype=float),
        A_ub=-A,
        b_ub=-demands,
        bounds=(0.0, None),
        method="highs",
    )
    if not result.success or result.x is None or result.fun is None:
        raise RuntimeError(f"restricted master LP failed: {result.message}")

    # The model uses -A x <= -d. SciPy reports objective sensitivity with respect
    # to that transformed RHS, so the economically natural demand prices are
    # the negatives of the reported inequality marginals.
    dual_prices = -np.asarray(result.ineqlin.marginals, dtype=float)
    dual_prices[np.abs(dual_prices) < 1e-12] = 0.0
    return MasterLPSolution(
        objective=float(result.fun),
        usage=np.asarray(result.x, dtype=float),
        dual_prices=dual_prices,
        message=str(result.message),
    )


def solve_integer_master(instance: CuttingStockInstance, patterns: list[Pattern]) -> IntegerMasterSolution:
    """Solve an integer master over a supplied finite pattern set."""
    A = pattern_matrix(patterns, instance.n_items)
    n_patterns = len(patterns)
    result = milp(
        c=np.ones(n_patterns, dtype=float),
        integrality=np.ones(n_patterns, dtype=int),
        bounds=Bounds(np.zeros(n_patterns), np.full(n_patterns, np.inf)),
        constraints=LinearConstraint(
            A,
            np.asarray(instance.demands, dtype=float),
            np.full(instance.n_items, np.inf),
        ),
        options={"disp": False},
    )
    if result.x is None or result.fun is None or result.status != 0:
        raise RuntimeError(f"integer master failed: {result.message}")
    return IntegerMasterSolution(
        objective=float(result.fun),
        usage=np.asarray(result.x, dtype=float),
        message=str(result.message),
    )
