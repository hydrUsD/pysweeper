"""L3 – Board I: Aufbau (Komposition, Minen legen, Nachbarn zählen)."""
from _helpers import cells, make_board, need


def board(width=4, height=3, mines=2):
    Board = need("pysweeper.board", "Board")
    return Board(width, height, mines)


def mines_of(b):
    return {(c.x, c.y) for c in cells(b) if c.is_mine}


def test_attributes():
    """Board(4, 3, 2) speichert width, height, mine_amount; mines_planted ist False"""
    b = board(4, 3, 2)
    assert (b.width, b.height, b.mine_amount) == (4, 3, 2), \
        f"Gefunden: width={b.width}, height={b.height}, mine_amount={b.mine_amount}"
    assert b.mines_planted is False, "Vor dem ersten Aufdecken sind noch keine Minen gelegt."


def test_grid_shape():
    """grid ist eine Liste aus height Zeilen mit je width Zellen"""
    b = board(4, 3, 2)
    assert isinstance(b.grid, list), "grid soll eine Liste (von Listen) sein, siehe Diagramm: List[List[Cell]]."
    assert len(b.grid) == 3, (f"grid hat {len(b.grid)} Zeilen, erwartet 3 (= height). "
                              f"Die äußere Liste sind die Zeilen: grid[y][x].")
    assert all(len(row) == 4 for row in b.grid), "Jede Zeile soll width = 4 Zellen haben."


def test_grid_cells():
    """grid[y][x] ist eine Cell, die ihre eigene Position (x, y) kennt"""
    Cell = need("pysweeper.cell", "Cell")
    b = board(4, 3, 2)
    for y in range(3):
        for x in range(4):
            cell = b.grid[y][x]
            assert isinstance(cell, Cell), f"grid[{y}][{x}] ist {type(cell).__name__}, keine Cell."
            assert (cell.x, cell.y) == (x, y), \
                f"grid[{y}][{x}] hat x={cell.x}, y={cell.y}. Sind x und y vertauscht?"


def test_grid_distinct_cells():
    """Jede Position hat ihr eigenes Cell-Objekt"""
    b = board(4, 3, 2)
    ids = {id(c) for c in cells(b)}
    assert len(ids) == 12, (f"Nur {len(ids)} verschiedene Cell-Objekte für 12 Felder. "
                            f"[[Cell(..)] * w] * h kopiert nur Referenzen; erzeuge jede Zelle einzeln "
                            f"(z. B. mit einer List Comprehension).")


def test_no_mines_before_reveal():
    """Nach dem Erzeugen liegen noch keine Minen"""
    assert not mines_of(board(9, 9, 10)), "Minen werden erst beim ersten Aufdecken gelegt."


def test_plant_mines_count():
    """_plant_mines legt genau mine_amount Minen und setzt mines_planted"""
    b = board(9, 9, 10)
    b._plant_mines(4, 4)
    assert len(mines_of(b)) == 10, f"{len(mines_of(b))} Minen gelegt, erwartet 10."
    assert b.mines_planted is True, "_plant_mines soll mines_planted auf True setzen."


def test_plant_mines_safe_zone():
    """Startzelle und ihre Nachbarn bleiben minenfrei"""
    for _ in range(30):
        b = board(9, 9, 10)
        b._plant_mines(0, 4)
        forbidden = {(x, y) for x in (0, 1) for y in (3, 4, 5)}
        hit = mines_of(b) & forbidden
        assert not hit, f"Mine auf {sorted(hit)}: Start (0, 4) und Nachbarn sollen sicher sein."


def test_plant_mines_crowded():
    """Zu wenig Platz (3x3, 8 Minen): nur die Startzelle bleibt sicher"""
    b = board(3, 3, 8)
    b._plant_mines(1, 1)
    assert len(mines_of(b)) == 8, "Auch wenn die Nachbarn nicht frei bleiben können: 8 Minen müssen liegen."
    assert (1, 1) not in mines_of(b), "Die Startzelle selbst muss immer sicher sein."


def test_plant_mines_random():
    """Die Minenverteilung ist zufällig"""
    layouts = set()
    for _ in range(10):
        b = board(9, 9, 10)
        b._plant_mines(4, 4)
        layouts.add(frozenset(mines_of(b)))
    assert len(layouts) > 1, "10 Bretter, immer dieselben Minen. Kommt der Zufall (random) zum Einsatz?"


def test_calculate_neighbors():
    """_calculate_neighbors zählt die Minen in den 8 Nachbarfeldern"""
    b = make_board(3, 3, {(0, 0), (2, 2)})
    numbers = {(c.x, c.y): c.neighbor_mines for c in cells(b) if not c.is_mine}
    expected = {(1, 0): 1, (2, 0): 0, (0, 1): 1, (1, 1): 2, (2, 1): 1, (0, 2): 0, (1, 2): 1}
    wrong = {pos: n for pos, n in numbers.items() if n != expected[pos]}
    assert not wrong, f"Falsche Zahlen {{(x, y): gefunden}}: {wrong}. Erwartet: {expected}"


def test_calculate_neighbors_not_square():
    """_calculate_neighbors funktioniert auf nicht-quadratischen Brettern (x/y nicht vertauscht)"""
    b = make_board(5, 2, {(4, 0)})
    assert b.grid[0][3].neighbor_mines == 1 and b.grid[1][3].neighbor_mines == 1 \
        and b.grid[1][4].neighbor_mines == 1, "Die Nachbarn von (4, 0) sollen 1 zeigen."
    assert b.grid[0][0].neighbor_mines == 0 and b.grid[1][2].neighbor_mines == 0, \
        "Felder weit weg von der Mine sollen 0 zeigen. Werden irgendwo x und y vertauscht?"


def test_calculate_neighbors_idempotent():
    """_calculate_neighbors zweimal aufrufen ändert nichts (setzt statt += zu zählen)"""
    b = make_board(3, 3, {(0, 0)})
    before = [c.neighbor_mines for c in cells(b) if not c.is_mine]
    b._calculate_neighbors()
    after = [c.neighbor_mines for c in cells(b) if not c.is_mine]
    assert before == after, ("Nach dem zweiten Aufruf haben sich die Zahlen verändert. Setze "
                             "neighbor_mines = Anzahl, statt mit += aufzuaddieren.")
