"""L7 Bonus – TkinterUI (nur Struktur, ohne Fenster zu öffnen)."""
import inspect

from _helpers import need


def test_tkinterui_inherits():
    """TkinterUI erbt von UserInterface und ist konkret"""
    UserInterface = need("pysweeper.ui.user_interface", "UserInterface")
    TkinterUI = need("pysweeper.ui.tkinter_ui", "TkinterUI")
    assert issubclass(TkinterUI, UserInterface)
    assert not inspect.isabstract(TkinterUI), \
        f"TkinterUI ist noch abstrakt, es fehlt: {sorted(TkinterUI.__abstractmethods__)}"


def test_tkinterui_callbacks():
    """TkinterUI hat _on_left_click(x, y) und _on_right_click(x, y)"""
    TkinterUI = need("pysweeper.ui.tkinter_ui", "TkinterUI")
    for name in ("_on_left_click", "_on_right_click", "_create_widgets"):
        assert callable(getattr(TkinterUI, name, None)), f"Methode {name} fehlt."
    params = list(inspect.signature(TkinterUI._on_left_click).parameters)
    assert params == ["self", "x", "y"], f"_on_left_click hat die Parameter {params}, erwartet (self, x, y)."


def test_same_game_two_uis():
    """Beide UIs nutzen pysweeper.game.Game, keine eigene Spiellogik-Kopie"""
    for module, name in (("pysweeper.ui.terminal_ui", "TerminalUI"), ("pysweeper.ui.tkinter_ui", "TkinterUI")):
        source = inspect.getsource(need(module))
        for forbidden in ("class Game", "class Board", "class Cell"):
            assert forbidden not in source, \
                f"{name} definiert `{forbidden}` selbst. Die UI soll die Klassen aus dem Paket benutzen."
