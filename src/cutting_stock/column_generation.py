from __future__ import annotations

from dataclasses import dataclass

from .data import CuttingStockInstance
from .master import MasterLPSolution, solve_master_lp
from .patterns import Pattern, initial_patterns
from .pricing import PricingResult, solve_pricing


@dataclass(frozen=True)
class IterationRecord:
    iteration: int
    master_objective: float
    pricing_dual_value: float
    reduced_cost: float
    generated_pattern: Pattern
    added: bool


@dataclass(frozen=True)
class ColumnGenerationResult:
    patterns: tuple[Pattern, ...]
    lp_solution: MasterLPSolution
    records: tuple[IterationRecord, ...]
    converged: bool

    @property
    def generated_columns(self) -> int:
        return sum(record.added for record in self.records)


def run_column_generation(
    instance: CuttingStockInstance,
    tolerance: float = 1e-9,
    max_iterations: int = 100,
) -> ColumnGenerationResult:
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    patterns = initial_patterns(instance)
    if not patterns:
        raise ValueError("no initial patterns can satisfy positive demand")
    records: list[IterationRecord] = []
    final_master: MasterLPSolution | None = None

    for iteration in range(1, max_iterations + 1):
        master = solve_master_lp(instance, patterns)
        pricing: PricingResult = solve_pricing(instance, master.dual_prices)
        improving = pricing.reduced_cost < -tolerance

        if improving and pricing.pattern in patterns:
            raise RuntimeError("pricing returned a duplicate negative-reduced-cost column")

        records.append(
            IterationRecord(
                iteration=iteration,
                master_objective=master.objective,
                pricing_dual_value=pricing.dual_value,
                reduced_cost=pricing.reduced_cost,
                generated_pattern=pricing.pattern,
                added=improving,
            )
        )

        if not improving:
            final_master = master
            return ColumnGenerationResult(
                patterns=tuple(patterns),
                lp_solution=final_master,
                records=tuple(records),
                converged=True,
            )
        patterns.append(pricing.pattern)

    final_master = solve_master_lp(instance, patterns)
    return ColumnGenerationResult(
        patterns=tuple(patterns),
        lp_solution=final_master,
        records=tuple(records),
        converged=False,
    )
