"""L4 Erweiterung – flags_placed, mine_revealed() und Chording."""
import inspect

from _helpers import make_board, need, revealed


def test_flags_placed_property():
    """flags_placed ist eine Property und zählt die Flaggen"""
    Board = need("pysweeper.board", "Board")
    assert isinstance(inspect.getattr_static(Board, "flags_placed", None), property), \
        "flags_placed soll mit @property definiert sein (Zugriff ohne Klammern)."
    b = make_board(4, 3, set())
    assert b.flags_placed == 0
    b.toggle_flag(0, 0)
    b.toggle_flag(3, 2)
    assert b.flags_placed == 2


def test_mine_revealed():
    """mine_revealed() ist False, bis eine Mine aufgedeckt wird"""
    b = make_board(5, 3, {(2, 0), (2, 1), (2, 2)})
    assert b.mine_revealed() is False
    b.reveal_cell(0, 0)
    assert b.mine_revealed() is False, "Die Cascade hat keine Mine aufgedeckt."
    b.reveal_cell(2, 1)
    assert b.mine_revealed() is True


def test_chord():
    """Chording: offene Zahl mit passenden Flaggen deckt die übrigen Nachbarn auf"""
    b = make_board(3, 3, {(0, 0)})
    b.reveal_cell(1, 1)
    b.toggle_flag(0, 0)
    assert b.reveal_cell(1, 1) is True, "Chording hat Zellen aufgedeckt, also True."
    expected = {(x, y) for x in range(3) for y in range(3)} - {(0, 0)}
    assert revealed(b) == expected, f"Aufgedeckt: {sorted(revealed(b))}"


def test_chord_wrong_flag_count():
    """Kein Chording, wenn die Anzahl der Flaggen nicht zur Zahl passt"""
    b = make_board(3, 3, {(0, 0)})
    b.reveal_cell(1, 1)
    assert b.reveal_cell(1, 1) is False
    assert revealed(b) == {(1, 1)}


def test_chord_wrong_flag_position():
    """Falsch gesetzte Flagge: Chording deckt die Mine auf"""
    b = make_board(3, 3, {(0, 0)})
    b.reveal_cell(1, 1)
    b.toggle_flag(2, 2)
    b.reveal_cell(1, 1)
    assert b.grid[0][0].is_revealed is True
    assert b.mine_revealed() is True


def test_chord_cascades():
    """Deckt Chording eine 0 auf, läuft die Cascade weiter"""
    b = make_board(5, 1, {(0, 0)})
    b.reveal_cell(1, 0)
    b.toggle_flag(0, 0)
    b.reveal_cell(1, 0)
    assert revealed(b) == {(1, 0), (2, 0), (3, 0), (4, 0)}, f"Aufgedeckt: {sorted(revealed(b))}"
