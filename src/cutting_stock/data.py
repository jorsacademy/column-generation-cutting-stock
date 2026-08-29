from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CuttingStockInstance:
    stock_length: int
    item_lengths: tuple[int, ...]
    demands: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.stock_length <= 0:
            raise ValueError("stock_length must be positive")
        if not self.item_lengths:
            raise ValueError("at least one item type is required")
        if len(self.item_lengths) != len(self.demands):
            raise ValueError("item_lengths and demands must have equal length")
        if any(length <= 0 for length in self.item_lengths):
            raise ValueError("item lengths must be positive")
        if any(length > self.stock_length for length in self.item_lengths):
            raise ValueError("every item must fit in one stock roll")
        if len(set(self.item_lengths)) != len(self.item_lengths):
            raise ValueError("item lengths must be unique")
        if any(demand < 0 for demand in self.demands):
            raise ValueError("demands must be nonnegative")
        if not any(self.demands):
            raise ValueError("at least one demand must be positive")

    @property
    def n_items(self) -> int:
        return len(self.item_lengths)


def demo_instance() -> CuttingStockInstance:
    """Return a compact instance that requires mixed cutting patterns."""
    return CuttingStockInstance(
        stock_length=110,
        item_lengths=(20, 45, 50, 55),
        demands=(48, 35, 24, 10),
    )
