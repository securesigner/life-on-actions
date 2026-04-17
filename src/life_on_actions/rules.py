"""Conway's Game of Life transition rule on a toroidal grid."""

from collections.abc import Iterable

Cell = tuple[int, int]


def tick(alive: Iterable[Cell], width: int, height: int) -> frozenset[Cell]:
    """Advance the board one generation with wrap-around edges."""
    alive_set = frozenset(alive)
    counts: dict[Cell, int] = {}
    for x, y in alive_set:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                neighbor = ((x + dx) % width, (y + dy) % height)
                counts[neighbor] = counts.get(neighbor, 0) + 1
    return frozenset(cell for cell, n in counts.items() if n == 3 or (n == 2 and cell in alive_set))
