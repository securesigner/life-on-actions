"""Entry point: read README → compute one Life tick → write README."""

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from life_on_actions.board import (
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    Board,
    parse_board,
    render_board,
    splice_board,
)
from life_on_actions.rules import tick


def main() -> int:
    readme_path = Path(os.environ.get("LIFE_README", "README.md"))
    readme = readme_path.read_text(encoding="utf-8")

    result = parse_board(readme, DEFAULT_WIDTH, DEFAULT_HEIGHT)
    board = result.board
    new_alive = tick(board.alive, board.width, board.height)

    # Stable board with no human edits to repair → stay quiet (heatmap rewards change).
    if new_alive == board.alive and not result.repairs:
        print("stable: board unchanged, skipping commit", file=sys.stderr)
        return 0

    births = len(new_alive - board.alive)
    deaths = len(board.alive - new_alive)
    new_board = Board(
        width=board.width,
        height=board.height,
        alive=new_alive,
        generation=board.generation + 1,
    )

    section = render_board(new_board, datetime.now(UTC))
    readme_path.write_text(splice_board(readme, section), encoding="utf-8")

    repair_note = f" · repaired {'; '.join(result.repairs)}" if result.repairs else ""
    print(
        f"tick: gen {new_board.generation} · "
        f"pop {new_board.population} (+{births} births, -{deaths} deaths)"
        f"{repair_note}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
