import pytest

from cutting_stock.column_generation import run_column_generation
from cutting_stock.data import CuttingStockInstance, demo_instance
from cutting_stock.master import solve_integer_master, solve_master_lp
from cutting_stock.patterns import enumerate_patterns
from cutting_stock.pricing import solve_pricing


def test_column_generation_matches_full_lp_on_demo():
    instance = demo_instance()
    cg = run_column_generation(instance)
    full = solve_master_lp(instance, enumerate_patterns(instance))
    assert cg.converged
    assert cg.lp_solution.objective == pytest.approx(full.objective, abs=1e-8)
    assert cg.records[-1].reduced_cost >= -1e-9
    assert cg.generated_columns > 0


def test_master_objective_is_nonincreasing_as_columns_are_added():
    cg = run_column_generation(demo_instance())
    objectives = [record.master_objective for record in cg.records]
    assert all(b <= a + 1e-9 for a, b in zip(objectives, objectives[1:]))


def test_final_duals_have_no_negative_reduced_cost_pattern():
    instance = demo_instance()
    cg = run_column_generation(instance)
    pricing = solve_pricing(instance, cg.lp_solution.dual_prices)
    assert pricing.reduced_cost >= -1e-9


def test_restricted_integer_master_matches_full_integer_on_demo():
    instance = demo_instance()
    cg = run_column_generation(instance)
    restricted = solve_integer_master(instance, list(cg.patterns))
    full = solve_integer_master(instance, enumerate_patterns(instance))
    assert restricted.objective == pytest.approx(40.0)
    assert restricted.objective == pytest.approx(full.objective)
    assert restricted.objective + 1e-9 >= cg.lp_solution.objective


def test_lp_column_generation_does_not_imply_integer_optimality():
    instance = CuttingStockInstance(8, (2, 3, 4), (1, 3, 1))
    cg = run_column_generation(instance)
    restricted = solve_integer_master(instance, list(cg.patterns))
    full = solve_integer_master(instance, enumerate_patterns(instance))
    assert cg.lp_solution.objective == pytest.approx(2.0)
    assert restricted.objective == pytest.approx(3.0)
    assert full.objective == pytest.approx(2.0)
