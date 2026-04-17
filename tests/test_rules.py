from life_on_actions.rules import tick


def test_empty_board_stays_empty():
    assert tick(frozenset(), 10, 10) == frozenset()


def test_block_is_still_life():
    block = frozenset({(1, 1), (1, 2), (2, 1), (2, 2)})
    assert tick(block, 10, 10) == block


def test_blinker_oscillates():
    horizontal = frozenset({(1, 2), (2, 2), (3, 2)})
    vertical = frozenset({(2, 1), (2, 2), (2, 3)})
    assert tick(horizontal, 10, 10) == vertical
    assert tick(vertical, 10, 10) == horizontal


def test_glider_translates():
    glider = frozenset({(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)})
    after_4 = glider
    for _ in range(4):
        after_4 = tick(after_4, 20, 20)
    # Glider moves +1 in x and +1 in y every 4 generations.
    expected = frozenset({(x + 1, y + 1) for (x, y) in glider})
    assert after_4 == expected


def test_toroidal_wrap():
    # Blinker straddling the right edge should still oscillate via wrap.
    horizontal = frozenset({(8, 2), (9, 2), (0, 2)})
    after = tick(horizontal, 10, 10)
    assert after == frozenset({(9, 1), (9, 2), (9, 3)})


def test_lone_cell_dies():
    assert tick(frozenset({(5, 5)}), 10, 10) == frozenset()
