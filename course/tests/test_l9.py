"""L9 – Offene und geschlossene Zellen in der TkinterUI unterscheidbar.

_cell_style wird ohne Fenster geprüft, die Klicks in einem unsichtbaren Fenster (Fixture tk_window in conftest.py).
"""
import inspect
import tkinter as tk

import pytest

from _helpers import make_board, need, revealed

KEYS = {"background": "bg", "foreground": "fg"}   # Langformen der Tk-Optionen auf die Kurzformen abbilden


def _ui(root=None):
    TkinterUI = need("pysweeper.ui.tkinter_ui", "TkinterUI")
    Game = need("pysweeper.game", "Game")
    EASY = need("pysweeper.difficulty_config", "EASY")
    ui = TkinterUI(root)
    ui.game = Game(EASY)
    return ui


def _cell(**state):
    cell = need("pysweeper.cell", "Cell")(0, 0)
    for name, value in state.items():
        setattr(cell, name, value)
    return cell


def _raw_style(ui, cell):
    if not callable(getattr(ui, "_cell_style", None)):
        pytest.fail("TkinterUI hat noch keine Methode _cell_style(cell).", pytrace=False)
    return ui._cell_style(cell)


def _style(ui, cell):
    style = _raw_style(ui, cell)
    assert isinstance(style, dict), f"_cell_style gibt {type(style).__name__} zurück, erwartet ein dict mit Tk-Optionen."
    style = {KEYS.get(k, k): v for k, v in style.items()}
    missing = {"text", "relief", "bg", "fg"} - set(style)
    assert not missing, f"Im dict von _cell_style fehlen {sorted(missing)} (gebraucht: text, relief, bg, fg)."
    return style


# ─────────────────────────────────────────────── _cell_style (ohne Fenster)

def test_cell_style_signature():
    """TkinterUI._cell_style(self, cell) gibt es"""
    TkinterUI = need("pysweeper.ui.tkinter_ui", "TkinterUI")
    assert callable(getattr(TkinterUI, "_cell_style", None)), "TkinterUI hat noch keine Methode _cell_style(cell)."
    params = list(inspect.signature(TkinterUI._cell_style).parameters)
    assert params == ["self", "cell"], f"_cell_style hat die Parameter {params}, erwartet (self, cell)."


def test_closed_and_flagged():
    """Geschlossen: relief raised, kein Text; Flagge: geschlossen mit „F“"""
    ui = _ui()
    closed = _style(ui, _cell())
    assert closed["relief"] == "raised", f"Geschlossene Zelle: relief {closed['relief']!r}, erwartet 'raised'."
    assert closed["text"] == "", f"Geschlossene Zelle zeigt {closed['text']!r}, erwartet ''."
    flag = _style(ui, _cell(is_flagged=True))
    assert flag["text"] == "F", f"Zelle mit Flagge zeigt {flag['text']!r}, erwartet 'F'."
    assert flag["relief"] == "raised", "Eine Flagge liegt auf einer geschlossenen Zelle: relief soll 'raised' bleiben."
    again = _style(ui, _cell())
    assert again["text"] == "", \
        f"Nach einer Flagge zeigt eine geschlossene Zelle {again['text']!r}. Ändert _cell_style den gemeinsamen " \
        f"Grundstil (CLOSED[\"text\"] = …)? Baue eine Kopie: {{**CLOSED, \"text\": \"F\"}}."


def test_open_differs_from_closed():
    """Offen: anderes relief und anderer Hintergrund als geschlossen, 0 ohne Text"""
    ui = _ui()
    closed = _style(ui, _cell())
    empty = _style(ui, _cell(is_revealed=True, neighbor_mines=0))
    assert empty["relief"] != "raised", "Offene Zelle hat relief 'raised' wie eine geschlossene. Nimm z. B. 'flat'."
    assert empty["bg"] != closed["bg"], \
        f"Offen und geschlossen haben denselben Hintergrund {closed['bg']!r}. Genau das soll L9 ändern."
    assert empty["text"] == "", f"Offene Zelle ohne Nachbarminen zeigt {empty['text']!r}, erwartet ''."


def test_numbers_have_colors():
    """Zahlen zeigen ihren Wert, 1, 2 und 3 in verschiedenen Farben"""
    ui = _ui()
    styles = {n: _style(ui, _cell(is_revealed=True, neighbor_mines=n)) for n in range(1, 9)}
    for n, style in styles.items():
        assert style["text"] == str(n), f"Offene Zelle mit {n} Nachbarminen zeigt {style['text']!r}, erwartet {str(n)!r}."
    colors = [styles[n]["fg"] for n in (1, 2, 3)]
    assert len(set(colors)) == 3, f"1, 2 und 3 haben die Textfarben {colors}. Sie sollen sich unterscheiden."


def test_open_mine():
    """Aufgedeckte Mine: „*“ auf eigenem Hintergrund"""
    ui = _ui()
    mine = _style(ui, _cell(is_revealed=True, is_mine=True))
    empty = _style(ui, _cell(is_revealed=True, neighbor_mines=0))
    assert mine["text"] == "*", f"Aufgedeckte Mine zeigt {mine['text']!r}, erwartet '*'."
    assert mine["bg"] != empty["bg"], "Eine aufgedeckte Mine hat denselben Hintergrund wie ein leeres Feld."


def test_styles_are_label_options(tk_window):
    """Jedes dict aus _cell_style lässt sich mit label.config(**style) anwenden"""
    ui = _ui()
    label = tk.Label(tk_window)
    states = [{}, {"is_flagged": True}, {"is_revealed": True}, {"is_revealed": True, "neighbor_mines": 3},
              {"is_revealed": True, "is_mine": True}]
    for state in states:
        try:
            label.config(**_raw_style(ui, _cell(**state)))
        except tk.TclError as e:
            pytest.fail(f"label.config(**_cell_style(…)) scheitert für eine Zelle mit {state or 'Startwerten'}: {e}",
                        pytrace=False)


# ─────────────────────────────────────────────── Widgets im (unsichtbaren) Fenster

def _ui_with_widgets(root):
    ui = _ui(root)
    try:
        ui._create_widgets(9, 9)
        ui.draw_board(ui.game.board)
    except AttributeError as e:
        pytest.fail(f"_create_widgets/draw_board scheitert: {e}. Heißt die Liste schon cells statt buttons?",
                    pytrace=False)
    root.update()
    if not hasattr(ui, "cells"):
        pytest.fail("TkinterUI hat kein Attribut cells. Benenne buttons in cells um.", pytrace=False)
    if not callable(getattr(ui, "_cell_style", None)):
        pytest.fail("TkinterUI hat noch keine Methode _cell_style(cell).", pytrace=False)
    return ui


def test_cells_are_labels(tk_window):
    """cells[y][x] ist ein 9×9-Raster aus tk.Label (keine Buttons mehr)"""
    ui = _ui_with_widgets(tk_window)
    cells = ui.cells
    assert len(cells) == 9 and all(len(row) == 9 for row in cells), "cells soll 9 Zeilen mit je 9 Zellen haben."
    kinds = {type(w).__name__ for row in cells for w in row}
    assert all(isinstance(w, tk.Label) for row in cells for w in row), \
        f"cells enthält {sorted(kinds)}, erwartet nur tk.Label (macOS-Buttons zeigen bg und relief nicht an)."


def test_left_click_reveals(tk_window):
    """Linksklick auf cells[2][6] deckt die Zelle (x=6, y=2) auf und zeichnet sie offen"""
    ui = _ui_with_widgets(tk_window)
    ui.game.board = make_board(9, 9, {(7, 2)})   # (6, 2) ist eine 1: der Klick deckt genau diese Zelle auf
    ui.draw_board(ui.game.board)
    ui.cells[2][6].event_generate("<Button-1>")
    tk_window.update()
    opened = revealed(ui.game.board)
    assert opened, "Ein Linksklick auf cells[2][6] deckt nichts auf. Ist <Button-1> per bind an _on_left_click gebunden?"
    assert opened == {(6, 2)}, \
        f"Ein Linksklick auf cells[2][6] deckt {sorted(opened)[:3]}… auf statt nur (x=6, y=2). Friert die lambda " \
        f"x und y ein (lambda e, x=x, y=y: …)? Sonst gilt für jede Zelle das letzte x und y der Schleife."
    assert ui.cells[2][6].cget("relief") != "raised", "Die aufgedeckte Zelle ist noch erhaben gezeichnet."


@pytest.mark.parametrize("event", ["<Button-2>", "<Button-3>"])
def test_right_click_flags(tk_window, event):
    """Rechtsklick setzt eine Flagge (macOS: <Button-2>, Windows/Linux: <Button-3>)"""
    ui = _ui_with_widgets(tk_window)
    ui.cells[0][1].event_generate(event)
    tk_window.update()
    assert ui.game.board.grid[0][1].is_flagged, \
        f"{event} auf cells[0][1] setzt keine Flagge. Binde beide Rechtsklick-Events an _on_right_click."
    assert ui.cells[0][1].cget("text") == "F"


def test_draw_board_applies_style(tk_window):
    """draw_board zeigt jede Zelle genau so, wie _cell_style sie beschreibt"""
    ui = _ui_with_widgets(tk_window)
    ui._on_left_click(4, 4)
    ui._on_right_click(*next((c.x, c.y) for row in ui.game.board.grid for c in row if not c.is_revealed))
    tk_window.update()
    for row in ui.game.board.grid:
        for cell in row:
            style = {KEYS.get(k, k): v for k, v in ui._cell_style(cell).items()}
            widget = ui.cells[cell.y][cell.x]
            for key in ("text", "relief", "bg", "fg"):
                assert str(widget.cget(key)) == str(style[key]), \
                    f"Zelle (x={cell.x}, y={cell.y}): {key} ist {widget.cget(key)!r}, _cell_style sagt " \
                    f"{style[key]!r}. Wendet draw_board das dict mit config(**style) an?"


def test_reset_closes_all(tk_window):
    """Nach reset_board() und draw_board ist wieder jede Zelle geschlossen"""
    ui = _ui_with_widgets(tk_window)
    ui._on_left_click(4, 4)
    ui.game.reset_board()
    ui.draw_board(ui.game.board)
    tk_window.update()
    still_open = [(x, y) for y, row in enumerate(ui.cells) for x, w in enumerate(row) if w.cget("relief") != "raised"]
    assert not still_open, f"Nach dem Neustart sehen noch {len(still_open)} Zellen offen aus, z. B. {still_open[0]}."
