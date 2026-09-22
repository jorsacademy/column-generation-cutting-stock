"""Steel plate cutting optimization with integer pattern selection.

The model:
- generates physically feasible 2D cutting patterns using explicit rectangle placement,
- uses integer decision variables (whole plates only),
- meets or exceeds demand,
- respects stock availability,
- minimizes plate + cutting + waste penalty cost.

This is still a compact educational model; it is not a full industrial nesting engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


@dataclass(frozen=True)
class Plate:
    width: int
    length: int
    cost: float
    available: int


@dataclass(frozen=True)
class Piece:
    width: int
    length: int
    demand: int
    priority: int = 1


@dataclass(frozen=True)
class Placement:
    piece_name: str
    x: int
    y: int
    width: int
    length: int
    rotated: bool


@dataclass
class CuttingPattern:
    id: int
    plate_type: str
    pieces: Dict[str, int]
    placements: List[Placement]
    cost: float
    waste_area: int


class SteelCuttingOptimizer:
    def __init__(self) -> None:
        self.stock_plates: Dict[str, Plate] = {
            "Large_Plate": Plate(width=200, length=300, cost=150.0, available=8),
            "Medium_Plate": Plate(width=150, length=250, cost=100.0, available=12),
            "Small_Plate": Plate(width=120, length=200, cost=75.0, available=15),
        }

        self.required_pieces: Dict[str, Piece] = {
            "Piece_A": Piece(width=60, length=80, demand=25, priority=1),
            "Piece_B": Piece(width=45, length=60, demand=30, priority=2),
            "Piece_C": Piece(width=70, length=90, demand=18, priority=1),
            "Piece_D": Piece(width=40, length=50, demand=35, priority=3),
            "Piece_E": Piece(width=55, length=75, demand=20, priority=2),
        }

        self.cutting_cost_per_piece = 2.5
        self.waste_penalty_per_cm2 = 0.8
        self.max_mixed_qty_per_type = 5
        self.max_single_qty = 15

        self.cutting_patterns = self.generate_cutting_patterns()

    @staticmethod
    def _prune_free_rectangles(
        rects: List[Tuple[int, int, int, int]],
    ) -> List[Tuple[int, int, int, int]]:
        unique = []
        for rect in rects:
            if rect[2] <= 0 or rect[3] <= 0:
                continue
            if rect not in unique:
                unique.append(rect)

        kept = []
        for i, current in enumerate(unique):
            cx, cy, cw, ch = current
            contained = False
            for j, other in enumerate(unique):
                if i == j:
                    continue
                ox, oy, ow, oh = other
                if (
                    ox <= cx
                    and oy <= cy
                    and ox + ow >= cx + cw
                    and oy + oh >= cy + ch
                ):
                    contained = True
                    break
            if not contained:
                kept.append(current)
        return kept

    def _try_maxrects_order(
        self,
        plate: Plate,
        item_names: List[str],
    ) -> List[Placement] | None:
        free_rects: List[Tuple[int, int, int, int]] = [
            (0, 0, plate.width, plate.length)
        ]
        placed: List[Placement] = []

        for name in item_names:
            piece = self.required_pieces[name]
            orientations = [(piece.width, piece.length, False)]
            if piece.width != piece.length:
                orientations.append((piece.length, piece.width, True))

            best = None
            for free_idx, (fx, fy, fw, fh) in enumerate(free_rects):
                for width, height, rotated in orientations:
                    if width <= fw and height <= fh:
                        short_side = min(fw - width, fh - height)
                        area_left = fw * fh - width * height
                        score = (short_side, area_left, fy, fx)
                        if best is None or score < best[0]:
                            best = (
                                score,
                                free_idx,
                                fx,
                                fy,
                                width,
                                height,
                                rotated,
                            )

            if best is None:
                return None

            _, _, x, y, width, height, rotated = best
            placement = Placement(name, x, y, width, height, rotated)
            placed.append(placement)

            px1, py1, px2, py2 = x, y, x + width, y + height
            new_free: List[Tuple[int, int, int, int]] = []

            for fx, fy, fw, fh in free_rects:
                rx1, ry1, rx2, ry2 = fx, fy, fx + fw, fy + fh

                if px2 <= rx1 or px1 >= rx2 or py2 <= ry1 or py1 >= ry2:
                    new_free.append((fx, fy, fw, fh))
                    continue

                if px1 > rx1:
                    new_free.append((rx1, ry1, px1 - rx1, fh))
                if px2 < rx2:
                    new_free.append((px2, ry1, rx2 - px2, fh))
                if py1 > ry1:
                    new_free.append((rx1, ry1, fw, py1 - ry1))
                if py2 < ry2:
                    new_free.append((rx1, py2, fw, ry2 - py2))

            free_rects = self._prune_free_rectangles(new_free)

        return placed

    def _pack_rectangles(
        self,
        plate: Plate,
        piece_counts: Dict[str, int],
    ) -> List[Placement] | None:
        """Return an explicit non-overlapping orthogonal placement if found.

        Several deterministic MaxRects-style item orders are tried. Every accepted
        pattern therefore has a concrete geometry; the heuristic can miss some
        feasible nestings but never accepts an area-only false positive.
        """
        items: List[str] = []
        for name, quantity in piece_counts.items():
            items.extend([name] * quantity)

        def area(name: str) -> int:
            piece = self.required_pieces[name]
            return piece.width * piece.length

        def long_side(name: str) -> int:
            piece = self.required_pieces[name]
            return max(piece.width, piece.length)

        def short_side(name: str) -> int:
            piece = self.required_pieces[name]
            return min(piece.width, piece.length)

        orders = [
            sorted(items, key=area, reverse=True),
            sorted(items, key=long_side, reverse=True),
            sorted(items, key=short_side, reverse=True),
        ]

        seen = set()
        for order in orders:
            key = tuple(order)
            if key in seen:
                continue
            seen.add(key)
            placement = self._try_maxrects_order(plate, order)
            if placement is not None:
                return placement
        return None

    def _pattern_cost(
        self,
        plate_name: str,
        piece_counts: Dict[str, int],
    ) -> Tuple[float, int]:
        plate = self.stock_plates[plate_name]
        plate_area = plate.width * plate.length
        used_area = sum(
            self.required_pieces[name].width
            * self.required_pieces[name].length
            * quantity
            for name, quantity in piece_counts.items()
        )
        waste_area = plate_area - used_area

        total_pieces = sum(piece_counts.values())
        cutting_cost = total_pieces * self.cutting_cost_per_piece
        waste_cost = waste_area * self.waste_penalty_per_cm2

        return plate.cost + cutting_cost + waste_cost, waste_area

    def _add_pattern(
        self,
        patterns: List[CuttingPattern],
        plate_name: str,
        counts: Dict[str, int],
    ) -> None:
        plate = self.stock_plates[plate_name]
        used_area = sum(
            self.required_pieces[name].width
            * self.required_pieces[name].length
            * quantity
            for name, quantity in counts.items()
        )
        if used_area > plate.width * plate.length:
            return

        placements = self._pack_rectangles(plate, counts)
        if placements is None:
            return

        cost, waste_area = self._pattern_cost(plate_name, counts)
        patterns.append(
            CuttingPattern(
                id=len(patterns),
                plate_type=plate_name,
                pieces=dict(counts),
                placements=placements,
                cost=cost,
                waste_area=waste_area,
            )
        )

    def generate_cutting_patterns(self) -> List[CuttingPattern]:
        patterns: List[CuttingPattern] = []
        piece_names = list(self.required_pieces)

        for plate_name, plate in self.stock_plates.items():
            for name in piece_names:
                piece = self.required_pieces[name]
                area_bound = (plate.width * plate.length) // (
                    piece.width * piece.length
                )
                max_qty = min(self.max_single_qty, int(area_bound))
                for quantity in range(1, max_qty + 1):
                    self._add_pattern(patterns, plate_name, {name: quantity})

            for first, second in combinations(piece_names, 2):
                for qty1 in range(1, self.max_mixed_qty_per_type + 1):
                    for qty2 in range(1, self.max_mixed_qty_per_type + 1):
                        self._add_pattern(
                            patterns,
                            plate_name,
                            {first: qty1, second: qty2},
                        )

        unique: Dict[
            Tuple[str, Tuple[Tuple[str, int], ...]], CuttingPattern
        ] = {}
        for pattern in patterns:
            key = (pattern.plate_type, tuple(sorted(pattern.pieces.items())))
            if key not in unique or pattern.cost < unique[key].cost:
                unique[key] = pattern

        result = list(unique.values())
        for index, pattern in enumerate(result):
            pattern.id = index
        return result

    def solve(self):
        if not self.cutting_patterns:
            raise RuntimeError("No feasible cutting patterns were generated.")

        pattern_count = len(self.cutting_patterns)
        piece_names = list(self.required_pieces)

        objective = np.array(
            [pattern.cost for pattern in self.cutting_patterns], dtype=float
        )

        constraints: List[LinearConstraint] = []

        demand_matrix = np.array(
            [
                [
                    pattern.pieces.get(piece_name, 0)
                    for pattern in self.cutting_patterns
                ]
                for piece_name in piece_names
            ],
            dtype=float,
        )
        demand_lb = np.array(
            [self.required_pieces[name].demand for name in piece_names],
            dtype=float,
        )
        constraints.append(
            LinearConstraint(demand_matrix, lb=demand_lb, ub=np.inf)
        )

        plate_names = list(self.stock_plates)
        availability_matrix = np.array(
            [
                [
                    1.0 if pattern.plate_type == plate_name else 0.0
                    for pattern in self.cutting_patterns
                ]
                for plate_name in plate_names
            ],
            dtype=float,
        )
        availability_ub = np.array(
            [self.stock_plates[name].available for name in plate_names],
            dtype=float,
        )
        constraints.append(
            LinearConstraint(
                availability_matrix,
                lb=0.0,
                ub=availability_ub,
            )
        )

        result = milp(
            c=objective,
            integrality=np.ones(pattern_count, dtype=int),
            bounds=Bounds(
                lb=np.zeros(pattern_count),
                ub=np.full(pattern_count, np.inf),
            ),
            constraints=constraints,
            options={"disp": False},
        )

        if not result.success or result.x is None:
            raise RuntimeError(f"Optimization failed: {result.message}")

        usage = np.rint(result.x).astype(int)
        return result, usage

    def print_solution(self, result, usage: np.ndarray) -> None:
        print("Steel Plate Cutting Optimization")
        print("=" * 40)
        print(f"Optimal total cost: ${result.fun:,.2f}")
        print(f"Solver status: {result.message}")

        print("\nSelected patterns:")
        total_plates = 0
        for pattern, count in zip(self.cutting_patterns, usage):
            if count <= 0:
                continue
            total_plates += int(count)
            plate = self.stock_plates[pattern.plate_type]
            utilization = 100.0 * (
                1.0
                - pattern.waste_area / (plate.width * plate.length)
            )
            print(
                f"P{pattern.id}: {count} x {pattern.plate_type} | "
                f"{pattern.pieces} | utilization={utilization:.1f}% | "
                f"cost/use=${pattern.cost:,.2f}"
            )

        print(f"\nTotal plates used: {total_plates}")

        print("\nDemand verification:")
        for piece_name, piece in self.required_pieces.items():
            produced = sum(
                int(count) * pattern.pieces.get(piece_name, 0)
                for pattern, count in zip(self.cutting_patterns, usage)
            )
            print(
                f"{piece_name}: produced={produced}, "
                f"demand={piece.demand}, surplus={produced - piece.demand}"
            )

    def visualize_most_used_pattern(self, usage: np.ndarray) -> None:
        if usage.max(initial=0) <= 0:
            return

        index = int(np.argmax(usage))
        pattern = self.cutting_patterns[index]
        plate = self.stock_plates[pattern.plate_type]

        fig, ax = plt.subplots(figsize=(8, 10))
        ax.add_patch(
            patches.Rectangle(
                (0, 0),
                plate.width,
                plate.length,
                linewidth=2,
                edgecolor="black",
                facecolor="none",
            )
        )

        for placement in pattern.placements:
            rect = patches.Rectangle(
                (placement.x, placement.y),
                placement.width,
                placement.length,
                linewidth=1,
                edgecolor="black",
                alpha=0.35,
            )
            ax.add_patch(rect)
            ax.text(
                placement.x + placement.width / 2,
                placement.y + placement.length / 2,
                placement.piece_name,
                ha="center",
                va="center",
                fontsize=8,
            )

        ax.set_xlim(0, plate.width)
        ax.set_ylim(0, plate.length)
        ax.set_aspect("equal")
        ax.set_title(
            f"Pattern P{pattern.id} on {pattern.plate_type} "
            f"(used {usage[index]} times)"
        )
        ax.set_xlabel("Width (cm)")
        ax.set_ylabel("Length (cm)")
        plt.tight_layout()
        plt.show()


def main() -> None:
    optimizer = SteelCuttingOptimizer()
    print(f"Generated {len(optimizer.cutting_patterns)} feasible patterns.")
    result, usage = optimizer.solve()
    optimizer.print_solution(result, usage)
    optimizer.visualize_most_used_pattern(usage)


if __name__ == "__main__":
    main()
