"""L2 – Cell."""
from _helpers import need


def test_position():
    """Cell(3, 5) speichert x=3 und y=5"""
    Cell = need("pysweeper.cell", "Cell")
    cell = Cell(3, 5)
    assert (cell.x, cell.y) == (3, 5), f"Gefunden: x={cell.x}, y={cell.y}"


def test_defaults():
    """Neue Zelle: keine Mine, verdeckt, nicht markiert, neighbor_mines = 0"""
    Cell = need("pysweeper.cell", "Cell")
    cell = Cell(0, 0)
    assert cell.is_mine is False, "is_mine soll anfangs False sein."
    assert cell.is_revealed is False, "is_revealed soll anfangs False sein."
    assert cell.is_flagged is False, "is_flagged soll anfangs False sein."
    assert cell.neighbor_mines == 0, "neighbor_mines soll anfangs 0 sein."


def test_instance_attributes():
    """Die Zustände sind Instanzattribute (in __init__ über self gesetzt)"""
    Cell = need("pysweeper.cell", "Cell")
    attributes = vars(Cell(0, 0))
    missing = [a for a in ("x", "y", "is_mine", "is_revealed", "is_flagged", "neighbor_mines")
               if a not in attributes]
    assert not missing, (f"{missing} sind keine Instanzattribute. Steht das direkt im Klassenrumpf? "
                         f"Dann gehören sie der Klasse (wie static in Java), nicht dem Objekt. "
                         f"Setze sie in __init__ mit self.<name> = ...")


def test_cells_independent():
    """Zwei Zellen teilen sich keinen Zustand"""
    Cell = need("pysweeper.cell", "Cell")
    a, b = Cell(0, 0), Cell(1, 0)
    a.is_flagged = True
    a.is_mine = True
    assert b.is_flagged is False and b.is_mine is False


def test_toggle_flag():
    """toggle_flag() schaltet die Markierung an und wieder aus"""
    Cell = need("pysweeper.cell", "Cell")
    cell = Cell(0, 0)
    cell.toggle_flag()
    assert cell.is_flagged is True, "Nach einem toggle_flag() soll is_flagged True sein."
    cell.toggle_flag()
    assert cell.is_flagged is False, "Nach dem zweiten toggle_flag() soll is_flagged wieder False sein."


def test_toggle_flag_revealed():
    """Eine aufgedeckte Zelle lässt sich nicht markieren"""
    Cell = need("pysweeper.cell", "Cell")
    cell = Cell(0, 0)
    cell.is_revealed = True
    cell.toggle_flag()
    assert cell.is_flagged is False, "Aufgedeckte Zellen bekommen keine Flagge (siehe main.py: toggle_flag)."
