"""Hilfsfunktionen für die Check-Tests."""
import importlib

import pytest


def _path(module):
    return module.replace(".", "/") + ".py"


def need(module, name=None):
    """Importiert `module` (und optional `name` daraus) mit verständlicher Fehlermeldung."""
    try:
        mod = importlib.import_module(module)
    except ModuleNotFoundError as e:
        if e.name and module.startswith(e.name):
            pytest.fail(f"Modul `{module}` nicht gefunden. Gibt es die Datei {_path(module)} "
                        f"(und ein __init__.py in jedem Paketordner)?", pytrace=False)
        pytest.fail(f"{_path(module)} importiert `{e.name}`, das gibt es nicht. Tippfehler im Import?",
                    pytrace=False)
    except Exception as e:
        pytest.fail(f"{_path(module)} lässt sich nicht importieren: {type(e).__name__}: {e}", pytrace=False)
    if name is None:
        return mod
    if not hasattr(mod, name):
        pytest.fail(f"In {_path(module)} gibt es noch kein `{name}`.", pytrace=False)
    return getattr(mod, name)


def make_board(width, height, mines):
    """Board mit festen Minenpositionen (set von (x, y)), damit nichts vom Zufall abhängt."""
    Board = need("pysweeper.board", "Board")
    board = Board(width, height, len(mines))
    for x, y in mines:
        board.grid[y][x].is_mine = True
    board.mines_planted = True
    board._calculate_neighbors()
    return board


def cells(board):
    return [cell for row in board.grid for cell in row]


def revealed(board):
    """Menge der aufgedeckten Positionen als (x, y)."""
    return {(c.x, c.y) for c in cells(board) if c.is_revealed}
