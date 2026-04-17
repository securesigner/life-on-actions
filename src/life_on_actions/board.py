"""Read and write the board inside a README.

Board lives between HTML-comment markers so the parser has an unambiguous anchor
even when humans edit the surrounding prose. Cells live inside a fenced code
block so GitHub doesn't reflow or linkify them.
"""

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

Cell = tuple[int, int]

ALIVE_GLYPH = "🟩"
DEAD_GLYPH = "⬛"

# ASCII fallbacks let humans hand-draw a pattern that the next tick re-renders as emoji.
_ALIVE_CHARS = frozenset({ALIVE_GLYPH, "#", "O", "*", "X", "x", "o"})
_DEAD_CHARS = frozenset({DEAD_GLYPH, ".", "_"})

START_MARKER = "<!-- life:board:start -->"
END_MARKER = "<!-- life:board:end -->"

DEFAULT_WIDTH = 40
DEFAULT_HEIGHT = 40

_CODE_BLOCK = re.compile(r"```(?:life)?\n(.*?)\n```", re.DOTALL)
_GENERATION = re.compile(r"Generation:\s*(\d+)")


class BoardParseError(Exception):
    """Raised when the README has no recoverable board."""


@dataclass(frozen=True)
class Board:
    width: int
    height: int
    alive: frozenset[Cell]
    generation: int = 0

    @property
    def population(self) -> int:
        return len(self.alive)


@dataclass(frozen=True)
class ParseResult:
    board: Board
    repairs: list[str] = field(default_factory=list)


def parse_board(
    readme: str,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> ParseResult:
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise BoardParseError(
            f"missing board markers: expected {START_MARKER!r} and {END_MARKER!r}"
        )

    section = readme[start + len(START_MARKER) : end]

    code = _CODE_BLOCK.search(section)
    if not code:
        raise BoardParseError("no fenced code block found between board markers")

    raw_rows = [line for line in code.group(1).split("\n") if line.strip()]

    alive: set[Cell] = set()
    repairs: list[str] = []
    unknown = 0
    short_rows = 0
    long_rows = 0

    for y, raw in enumerate(raw_rows[:height]):
        line = "".join(raw.split())  # tolerate spaces between hand-drawn cells
        if len(line) < width:
            short_rows += 1
        elif len(line) > width:
            long_rows += 1
        for x in range(min(len(line), width)):
            c = line[x]
            if c in _ALIVE_CHARS:
                alive.add((x, y))
            elif c not in _DEAD_CHARS:
                unknown += 1

    if len(raw_rows) < height:
        repairs.append(f"padded {height - len(raw_rows)} missing rows")
    if len(raw_rows) > height:
        repairs.append(f"truncated {len(raw_rows) - height} excess rows")
    if short_rows:
        repairs.append(f"padded {short_rows} short rows")
    if long_rows:
        repairs.append(f"truncated {long_rows} long rows")
    if unknown:
        repairs.append(f"treated {unknown} unknown glyphs as dead")

    gen_match = _GENERATION.search(section)
    generation = int(gen_match.group(1)) if gen_match else 0

    return ParseResult(
        board=Board(width=width, height=height, alive=frozenset(alive), generation=generation),
        repairs=repairs,
    )


def render_board(board: Board, updated: datetime | None = None) -> str:
    """Render the section that replaces everything between the markers."""
    when = (updated or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = [
        "".join(ALIVE_GLYPH if (x, y) in board.alive else DEAD_GLYPH for x in range(board.width))
        for y in range(board.height)
    ]
    grid = "\n".join(rows)
    meta = f"`Generation: {board.generation} · Population: {board.population} · Updated: {when}`"
    return f"\n\n```life\n{grid}\n```\n\n{meta}\n\n"


def splice_board(readme: str, rendered_section: str) -> str:
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start == -1 or end == -1:
        raise BoardParseError("markers missing; cannot splice board")
    return readme[: start + len(START_MARKER)] + rendered_section + readme[end:]
