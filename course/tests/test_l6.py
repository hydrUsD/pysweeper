"""L6 – UserInterface (ABC), TerminalUI und __main__."""
import ast
import curses
import importlib
import inspect
import sys

import pytest

from _helpers import need


def test_userinterface_abstract():
    """UserInterface ist abstrakt: run und draw_board sind @abstractmethod"""
    UserInterface = need("pysweeper.ui.user_interface", "UserInterface")
    abstract = set(getattr(UserInterface, "__abstractmethods__", set()))
    assert abstract == {"run", "draw_board"}, \
        f"Abstrakte Methoden: {sorted(abstract) or 'keine'}. Erbt die Klasse von ABC und sind beide " \
        f"Methoden mit @abstractmethod markiert?"
    with pytest.raises(TypeError):
        UserInterface()
        pytest.fail("UserInterface() ließ sich instanziieren. Abstrakte Klassen dürfen das nicht.",
                    pytrace=False)


def test_subclass_must_implement_all():
    """Eine Unterklasse ohne draw_board bleibt abstrakt"""
    UserInterface = need("pysweeper.ui.user_interface", "UserInterface")

    class HalfUI(UserInterface):
        def run(self, game):
            pass

    class FullUI(HalfUI):
        def draw_board(self, board):
            pass

    with pytest.raises(TypeError):
        HalfUI()
    FullUI()


def test_terminalui_inherits():
    """TerminalUI erbt von UserInterface und ist konkret"""
    UserInterface = need("pysweeper.ui.user_interface", "UserInterface")
    TerminalUI = need("pysweeper.ui.terminal_ui", "TerminalUI")
    assert issubclass(TerminalUI, UserInterface), "class TerminalUI(UserInterface): ..."
    assert not inspect.isabstract(TerminalUI), \
        f"TerminalUI ist noch abstrakt, es fehlt: {sorted(TerminalUI.__abstractmethods__)}"


def test_terminalui_init_only_stores():
    """TerminalUI(stdscr) speichert nur, curses wird erst in run() eingerichtet"""
    TerminalUI = need("pysweeper.ui.terminal_ui", "TerminalUI")
    fake_stdscr = object()
    try:
        ui = TerminalUI(fake_stdscr)
    except Exception as e:
        pytest.fail(f"TerminalUI(stdscr) wirft {type(e).__name__}: {e}. Der Konstruktor soll nur "
                    f"Attribute setzen; curses-Setup gehört nach _setup_curses() in run().", pytrace=False)
    assert ui.stdscr is fake_stdscr, "TerminalUI soll stdscr als self.stdscr speichern."
    assert isinstance(ui.cursor_x, int) and isinstance(ui.cursor_y, int), \
        "__init__ soll cursor_x und cursor_y als ganze Zahlen setzen (Start: 0, 0)."


@pytest.mark.parametrize("difficulty, max_x, max_y", [("EASY", 8, 8), ("HARD", 29, 15)], ids=["EASY", "HARD"])
def test_move_cursor_clamps(difficulty, max_x, max_y):
    """_move_cursor bleibt innerhalb des Bretts"""
    TerminalUI = need("pysweeper.ui.terminal_ui", "TerminalUI")
    Game = need("pysweeper.game", "Game")
    ui = TerminalUI(object())
    ui.game = Game(need("pysweeper.difficulty_config", difficulty))
    ui.cursor_x, ui.cursor_y = 0, 0
    ui._move_cursor(-1, -1)
    assert (ui.cursor_x, ui.cursor_y) == (0, 0), "Der Cursor darf nicht über den Rand nach links/oben."
    ui._move_cursor(100, 100)
    assert (ui.cursor_x, ui.cursor_y) == (max_x, max_y), \
        f"Cursor bei ({ui.cursor_x}, {ui.cursor_y}), erwartet ({max_x}, {max_y}). " \
        f"Begrenzt du x mit width und y mit height (über self.game.board)?"
    ui._move_cursor(-1, 0)
    assert (ui.cursor_x, ui.cursor_y) == (max_x - 1, max_y)


@pytest.mark.parametrize("module", ["pysweeper.cell", "pysweeper.board", "pysweeper.game"])
def test_logic_does_not_know_ui(module):
    """Die Spiellogik importiert weder curses noch das ui-Paket"""
    mod = need(module)
    tree = ast.parse(inspect.getsource(mod))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            base = "." * node.level + (node.module or "")
            imported.add(base)
            imported |= {f"{base}.{alias.name}" for alias in node.names}

    def is_ui(name):
        parts = name.lstrip(".").split(".")
        return parts[0] in ("curses", "tkinter") or "ui" in parts

    bad = sorted(name for name in imported if is_ui(name))
    assert not bad, f"{module} importiert {bad}. Die Abhängigkeit soll nur UI → Logik zeigen, nie zurück."


def test_main_module_guarded(monkeypatch):
    """pysweeper/__main__.py startet das Spiel nur bei `python -m pysweeper`, nicht beim Import"""
    def boom(*args, **kwargs):
        raise RuntimeError("curses.wrapper wurde beim Import aufgerufen")
    monkeypatch.setattr(curses, "wrapper", boom)
    sys.modules.pop("pysweeper.__main__", None)
    try:
        mod = importlib.import_module("pysweeper.__main__")
    except ModuleNotFoundError as e:
        if e.name == "pysweeper.__main__":
            pytest.fail("pysweeper/__main__.py fehlt noch.", pytrace=False)
        pytest.fail(f"pysweeper/__main__.py importiert `{e.name}`, das gibt es nicht. Tippfehler im Import?",
                    pytrace=False)
    except RuntimeError:
        pytest.fail("Beim bloßen Import startet schon das Spiel. Pack den Start in "
                    "if __name__ == \"__main__\": ...", pytrace=False)

    def calls_wrapper(node):
        return any(isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", None)) == "wrapper"
                   for n in ast.walk(node))

    guards = [n for n in ast.walk(ast.parse(inspect.getsource(mod)))
              if isinstance(n, ast.If) and "__name__" in ast.unparse(n.test)]
    assert any(calls_wrapper(g) for g in guards), \
        "In __main__.py fehlt unter if __name__ == \"__main__\": der Start per curses.wrapper(...)."
