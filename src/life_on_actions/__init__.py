"""Conway's Game of Life, ticked by GitHub Actions cron."""

from life_on_actions.board import Board, parse_board, render_board
from life_on_actions.rules import tick

__all__ = ["Board", "parse_board", "render_board", "tick"]
