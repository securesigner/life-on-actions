"""One-off: write the starter README with Gosper's glider gun already running."""

from datetime import UTC, datetime
from pathlib import Path

from life_on_actions.board import (
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    END_MARKER,
    START_MARKER,
    Board,
    render_board,
)

# Gosper's glider gun, (x, y) pairs. 36 wide × 9 tall, positioned near the top-left.
GOSPER = frozenset(
    {
        (1, 5),
        (1, 6),
        (2, 5),
        (2, 6),
        (11, 5),
        (11, 6),
        (11, 7),
        (12, 4),
        (12, 8),
        (13, 3),
        (13, 9),
        (14, 3),
        (14, 9),
        (15, 6),
        (16, 4),
        (16, 8),
        (17, 5),
        (17, 6),
        (17, 7),
        (18, 6),
        (21, 3),
        (21, 4),
        (21, 5),
        (22, 3),
        (22, 4),
        (22, 5),
        (23, 2),
        (23, 6),
        (25, 1),
        (25, 2),
        (25, 6),
        (25, 7),
        (35, 3),
        (35, 4),
        (36, 3),
        (36, 4),
    }
)

PROSE_TOP = """\
# life-on-actions

**Conway's Game of Life, ticked every 10 minutes by a GitHub Actions cron.**
No servers. No database. The README *is* the board.

"""

PROSE_BOTTOM = """\
## What is this?

Every ten minutes, a scheduled workflow wakes up, reads the board out of this
README, computes one generation of Conway's Game of Life, and commits the new
state back to the same branch. The contribution heatmap on the repo homepage
becomes a vitality indicator — still lifes go quiet, oscillators and gliders
keep committing, and extinction leaves a dead strip on the calendar.

Forking the repo seeds a new universe. Each fork's README evolves
independently; the heatmap tells you which universes are alive.

## Start your own universe

1. **Fork this repo.**
2. Open the **Actions** tab on your fork and click the green banner
   *"I understand my workflows, enable them"* — GitHub disables scheduled
   workflows on new forks until you do.
3. Open the `tick` workflow and hit **Run workflow** once if you don't want to
   wait ten minutes for the first generation.
4. Edit `README.md` any time to reseed. Draw with `#` and `.` if you don't
   want to paste emoji — the next tick re-renders it all into squares.

That's it. No secrets, no setup, no external services.

## How it works

- The board lives between `<!-- life:board:start -->` and
  `<!-- life:board:end -->` markers inside a fenced code block so GitHub
  renders it as a tidy grid and the parser has an unambiguous anchor.
- [`src/life_on_actions`](src/life_on_actions) implements the parser, the
  toroidal Life rule, and the renderer.
- [`.github/workflows/tick.yml`](.github/workflows/tick.yml) runs on
  `schedule` only — never on `push` — so a bot commit cannot trigger another
  tick. Commits also carry `[skip ci]` as a second line of defense.
- The parser tolerates human edits: ragged rows are padded, extra rows get
  truncated, unknown glyphs count as dead, and spaces between ASCII cells are
  ignored. Whatever you leave behind, the next tick cleans up.
- The grid is toroidal (edges wrap), so gliders don't just sail off and leave
  a dead universe behind.

## Development

```sh
uv sync
uv run pytest
uv run ruff check
uv run tick       # compute one tick in place
```

## Credits

Conway's Game of Life (1970). Gosper's glider gun (1970). GitHub Actions (2018).
"""


def main() -> None:
    board = Board(
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        alive=GOSPER,
        generation=0,
    )
    section = render_board(board, datetime(2026, 4, 17, 0, 0, 0, tzinfo=UTC))
    readme = f"{PROSE_TOP}{START_MARKER}{section}{END_MARKER}\n\n{PROSE_BOTTOM}"
    Path("README.md").write_text(readme, encoding="utf-8")
    print(f"seeded: {board.population} live cells")


if __name__ == "__main__":
    main()
