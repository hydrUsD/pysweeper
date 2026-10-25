"""L4 – Board II: Verhalten (reveal_cell, Cascade, toggle_flag, check_win)."""
from _helpers import cells, make_board, need, revealed

# 5x3-Brett mit einer Minen-"Wand" in Spalte x=2:
#   x: 0 1 2 3 4
#      . 2 * 2 .     y=0
#      . 3 * 3 .     y=1
#      . 2 * 2 .     y=2
WALL = {(2, 0), (2, 1), (2, 2)}


def test_first_reveal_plants_mines():
    """Erstes reveal_cell legt die Minen und deckt eine sichere Startzelle auf"""
    Board = need("pysweeper.board", "Board")
    b = Board(9, 9, 10)
    result = b.reveal_cell(3, 5)
    assert b.mines_planted is True, "Das erste reveal_cell soll die Minen legen (_plant_mines)."
    assert sum(c.is_mine for c in cells(b)) == 10, "Nach dem ersten Aufdecken sollen 10 Minen liegen."
    assert b.grid[5][3].is_mine is False, "Die Startzelle darf keine Mine sein."
    assert b.grid[5][3].is_revealed is True, "Die Startzelle soll aufgedeckt sein."
    assert result is True, "reveal_cell soll True zurückgeben, wenn die Zelle aufgedeckt wurde."


def test_first_reveal_counts_neighbors():
    """Nach dem ersten reveal_cell stimmen die neighbor_mines-Zahlen"""
    Board = need("pysweeper.board", "Board")
    b = Board(9, 9, 10)
    b.reveal_cell(4, 4)
    for c in cells(b):
        if c.is_mine:
            continue
        count = sum(b.grid[y][x].is_mine
                    for x in range(c.x - 1, c.x + 2) for y in range(c.y - 1, c.y + 2)
                    if 0 <= x < 9 and 0 <= y < 9 and (x, y) != (c.x, c.y))
        assert c.neighbor_mines == count, \
            f"Zelle ({c.x}, {c.y}) zeigt {c.neighbor_mines}, hat aber {count} Minen-Nachbarn. " \
            f"Wird _calculate_neighbors nach _plant_mines aufgerufen?"


def test_reveal_number():
    """Aufdecken einer Zahl deckt nur diese eine Zelle auf"""
    b = make_board(5, 3, WALL)
    assert b.reveal_cell(1, 1) is True
    assert revealed(b) == {(1, 1)}, f"Aufgedeckt: {sorted(revealed(b))}, erwartet nur (1, 1)."


def test_reveal_mine():
    """Aufdecken einer Mine: Zelle ist offen, reveal_cell gibt True zurück"""
    b = make_board(5, 3, WALL)
    assert b.reveal_cell(2, 1) is True, "Auch eine Mine wird aufgedeckt, also True."
    assert b.grid[1][2].is_revealed is True


def test_reveal_isolated_mine_no_cascade():
    """Von einer Mine aus wird nie weiter aufgedeckt, auch wenn neighbor_mines == 0"""
    b = make_board(4, 4, {(0, 0)})
    b.reveal_cell(0, 0)
    assert revealed(b) == {(0, 0)}, ("Nach dem Aufdecken der Mine (0, 0) ist mehr offen: "
                                     f"{sorted(revealed(b))}. Eine Mine hat oft neighbor_mines == 0, "
                                     "die Cascade darf trotzdem nur bei Nicht-Minen starten.")


def test_cascade():
    """Eine 0 deckt per Cascade alle angrenzenden Felder auf, stoppt an Zahlen"""
    b = make_board(5, 3, WALL)
    b.reveal_cell(0, 0)
    left = {(x, y) for x in (0, 1) for y in range(3)}
    assert revealed(b) == left, (f"Aufgedeckt: {sorted(revealed(b))}. Erwartet: die Spalten x=0 und "
                                 f"x=1 (die Nullen und ihre Zahlen-Ränder), nicht die Minen-Wand.")


def test_cascade_skips_flags():
    """Die Cascade deckt keine markierten Zellen auf"""
    b = make_board(5, 3, WALL)
    b.toggle_flag(1, 2)
    b.reveal_cell(0, 0)
    assert b.grid[2][1].is_revealed is False and b.grid[2][1].is_flagged is True, \
        "Die markierte Zelle (1, 2) wurde von der Cascade aufgedeckt."


def test_cascade_large_board():
    """Cascade auf einem großen leeren Brett (60x60) ohne RecursionError"""
    b = make_board(60, 60, {(59, 59)})
    b.reveal_cell(0, 0)
    assert len(revealed(b)) == 60 * 60 - 1, "Es sollen alle Felder außer der Mine aufgedeckt sein."


def test_reveal_flagged():
    """reveal_cell auf einer markierten Zelle tut nichts und gibt False zurück"""
    b = make_board(5, 3, WALL)
    b.toggle_flag(0, 0)
    assert b.reveal_cell(0, 0) is False
    assert not revealed(b), "Markierte Zellen dürfen nicht aufgedeckt werden."


def test_reveal_flagged_before_first_click():
    """Erster Klick auf eine markierte Zelle legt noch keine Minen"""
    Board = need("pysweeper.board", "Board")
    b = Board(9, 9, 10)
    b.toggle_flag(0, 0)
    assert b.reveal_cell(0, 0) is False
    assert b.mines_planted is False, "Erst prüfen, ob markiert, dann Minen legen (wie in main.py)."


def test_reveal_already_revealed():
    """reveal_cell auf einer schon offenen Zelle (ohne passende Flaggen) gibt False zurück"""
    b = make_board(5, 3, WALL)
    b.reveal_cell(1, 1)
    assert b.reveal_cell(1, 1) is False, "Es wurde nichts Neues aufgedeckt, also False."
    assert revealed(b) == {(1, 1)}


def test_toggle_flag():
    """Board.toggle_flag(x, y) markiert und entmarkiert die richtige Zelle"""
    b = make_board(4, 3, set())
    b.toggle_flag(3, 1)
    assert b.grid[1][3].is_flagged is True, "toggle_flag(3, 1) soll grid[1][3] markieren."
    b.toggle_flag(3, 1)
    assert b.grid[1][3].is_flagged is False


def test_check_win():
    """check_win: True genau dann, wenn alle Nicht-Minen aufgedeckt sind"""
    b = make_board(3, 1, {(0, 0)})
    assert b.check_win() is False
    b.reveal_cell(1, 0)
    assert b.check_win() is False, "(2, 0) ist noch verdeckt."
    b.reveal_cell(2, 0)
    assert b.check_win() is True


def test_check_win_flags_irrelevant():
    """Alle Minen markieren reicht nicht zum Sieg"""
    b = make_board(3, 1, {(0, 0)})
    b.toggle_flag(0, 0)
    assert b.check_win() is False, "Gewonnen ist erst, wenn alle sicheren Felder offen sind."


def test_check_win_is_query():
    """check_win verändert nichts (reine Abfrage)"""
    b = make_board(3, 1, {(0, 0)})
    b.reveal_cell(1, 0)
    b.reveal_cell(2, 0)
    before = [(c.is_mine, c.is_revealed, c.is_flagged, c.neighbor_mines) for c in cells(b)]
    b.check_win()
    after = [(c.is_mine, c.is_revealed, c.is_flagged, c.neighbor_mines) for c in cells(b)]
    assert before == after, "check_win hat Zellen verändert. Eine Abfrage darf keinen Zustand ändern."
