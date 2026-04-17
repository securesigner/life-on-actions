import pytest

from life_on_actions.board import (
    END_MARKER,
    START_MARKER,
    Board,
    BoardParseError,
    parse_board,
    render_board,
    splice_board,
)


def _wrap(body: str) -> str:
    return f"# heading\n\n{START_MARKER}\n{body}\n{END_MARKER}\n\nfooter\n"


def test_round_trip_emoji():
    board = Board(width=5, height=3, alive=frozenset({(0, 0), (1, 1), (4, 2)}), generation=7)
    readme = _wrap(render_board(board).strip())
    result = parse_board(readme, width=5, height=3)
    assert result.board.alive == board.alive
    assert result.board.generation == 7
    assert result.repairs == []


def test_ascii_fallback_is_parsed():
    body = "```life\n#.#\n.#.\n#.#\n```\n"
    result = parse_board(_wrap(body), width=3, height=3)
    assert result.board.alive == frozenset({(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)})


def test_spaces_between_cells_are_ignored():
    body = "```life\n# . #\n. # .\n# . #\n```\n"
    result = parse_board(_wrap(body), width=3, height=3)
    assert result.board.alive == frozenset({(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)})


def test_short_rows_are_padded_and_reported():
    body = "```life\n##\n##\n##\n```\n"
    result = parse_board(_wrap(body), width=5, height=3)
    assert result.board.alive == frozenset({(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)})
    assert any("short rows" in r for r in result.repairs)


def test_excess_rows_are_truncated():
    body = "```life\n#\n#\n#\n#\n#\n```\n"
    result = parse_board(_wrap(body), width=1, height=3)
    assert result.board.alive == frozenset({(0, 0), (0, 1), (0, 2)})
    assert any("excess rows" in r for r in result.repairs)


def test_unknown_glyph_treated_as_dead():
    body = "```life\n#?#\n```\n"
    result = parse_board(_wrap(body), width=3, height=1)
    assert result.board.alive == frozenset({(0, 0), (2, 0)})
    assert any("unknown glyphs" in r for r in result.repairs)


def test_missing_markers_raises():
    with pytest.raises(BoardParseError):
        parse_board("no markers here", width=5, height=5)


def test_missing_code_block_raises():
    readme = _wrap("no code block between the markers")
    with pytest.raises(BoardParseError):
        parse_board(readme, width=5, height=5)


def test_splice_preserves_surrounding_prose():
    board = Board(width=3, height=1, alive=frozenset({(0, 0), (2, 0)}), generation=1)
    before = _wrap("```life\n...\n```\n")
    after = splice_board(before, render_board(board))
    assert after.startswith("# heading\n\n")
    assert after.endswith("\nfooter\n")
    assert START_MARKER in after
    assert END_MARKER in after
    assert "🟩" in after


def test_generation_is_parsed_from_metadata_line():
    body = "```life\n#\n```\n`Generation: 42 · Population: 1 · Updated: now`\n"
    result = parse_board(_wrap(body), width=1, height=1)
    assert result.board.generation == 42
