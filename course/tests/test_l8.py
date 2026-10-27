"""L8 – StartMenu (Tkinter) und LAUNCHERS in __main__.py.

Die StartMenu-Tests öffnen ein verstecktes Tk-Fenster (Fixture tk_root in conftest.py).
"""
import curses
import importlib
import inspect
import runpy
import sys
import tkinter as tk

import pytest

from _helpers import need

NAMES = ["Alpha", "Beta"]   # erfundene UI-Namen: StartMenu soll keine Namen fest eingebaut haben


def _difficulties():
    return list(need("pysweeper.difficulty_config", "DIFFICULTIES"))


def _by_name(name):
    return next(d for d in _difficulties() if d.name == name)


def _menu_difficulties():
    """Erfundene Liste: StartMenu soll die übergebenen Schwierigkeiten zeigen, nicht DIFFICULTIES importieren."""
    DifficultyConfig = need("pysweeper.difficulty_config", "DifficultyConfig")
    return [DifficultyConfig("Mini", 1, (2, 2)), _by_name("Medium"), _by_name("Hard")]


def _menu(root, names=NAMES):
    StartMenu = need("pysweeper.ui.start_menu", "StartMenu")
    try:
        return StartMenu(root, names, _menu_difficulties())
    except Exception as e:
        hint = ""
        if isinstance(e, AttributeError) and ("'tk'" in str(e) or "'master'" in str(e)):
            hint = (" Ruft __init__ als Erstes super().__init__(master) auf? Ohne das fehlt dem Frame sein "
                    "Tk-Innenleben.")
        pytest.fail(f"StartMenu(root, {names}, difficulties) scheitert: {type(e).__name__}: {e}.{hint}",
                    pytrace=False)


def _descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from _descendants(child)


def _radios_for(menu, variable):
    """Radiobuttons, die an `variable` gebunden sind, egal wie tief sie verschachtelt sind."""
    return [w for w in _descendants(menu)
            if isinstance(w, tk.Radiobutton) and str(w.cget("variable")) == str(variable)]


def _destroyed(root):
    try:
        root.winfo_exists()
    except tk.TclError:
        return True
    return False


# ─────────────────────────────────────────────── StartMenu

def test_startmenu_is_frame():
    """StartMenu in pysweeper/ui/start_menu.py erbt von tk.Frame"""
    StartMenu = need("pysweeper.ui.start_menu", "StartMenu")
    assert issubclass(StartMenu, tk.Frame), \
        "StartMenu soll von tk.Frame erben: class StartMenu(tk.Frame): ..."


def test_init_calls_super(tk_root):
    """StartMenu(master, ui_names, difficulties) ruft super().__init__(master) auf und speichert die Listen"""
    menu = _menu(tk_root)
    assert menu.master is tk_root, \
        "menu.master ist nicht das übergebene Fenster. Reichst du master an super().__init__(master) weiter?"
    assert list(menu.ui_names) == NAMES
    assert list(menu.difficulties) == _menu_difficulties(), \
        "menu.difficulties ist nicht die übergebene Liste. Speichere den Parameter difficulties, statt " \
        "DIFFICULTIES zu importieren."


def test_variables_start_values(tk_root):
    """ui_choice und difficulty_choice sind tk.StringVar mit dem ersten Eintrag als Startwert"""
    menu = _menu(tk_root)
    for name in ("ui_choice", "difficulty_choice"):
        assert isinstance(getattr(menu, name, None), tk.StringVar), f"menu.{name} soll ein tk.StringVar sein."
    assert menu.ui_choice.get() == NAMES[0], \
        f"ui_choice startet mit {menu.ui_choice.get()!r}, erwartet wird der erste UI-Name {NAMES[0]!r}."
    first = _menu_difficulties()[0].name
    assert menu.difficulty_choice.get() == first, \
        f"difficulty_choice startet mit {menu.difficulty_choice.get()!r}, erwartet wird {first!r} " \
        f"(der Name der ersten übergebenen Schwierigkeit, nicht das Objekt)."
    assert menu.selection is None, "Vor dem Klick auf Start soll selection None sein."


def test_radiobuttons_for_ui_names(tk_root):
    """Ein Radiobutton pro UI-Name, gebunden an ui_choice"""
    menu = _menu(tk_root)
    radios = _radios_for(menu, menu.ui_choice)
    texts = sorted(r.cget("text") for r in radios)
    assert texts == sorted(NAMES), \
        f"Radiobuttons an ui_choice: {texts}, erwartet {sorted(NAMES)}. Die Namen kommen aus ui_names, " \
        f"nicht fest aus dem Code."
    next(r for r in radios if r.cget("text") == "Beta").invoke()
    assert menu.ui_choice.get() == "Beta", "Klick auf „Beta“ ändert ui_choice nicht. Hat der Radiobutton value=name?"


def test_radiobuttons_for_difficulties(tk_root):
    """Ein Radiobutton pro übergebener Schwierigkeit, gebunden an difficulty_choice (value = Name)"""
    menu = _menu(tk_root)
    radios = _radios_for(menu, menu.difficulty_choice)
    expected = _menu_difficulties()
    assert len(radios) == len(expected), \
        f"{len(radios)} Radiobuttons an difficulty_choice, erwartet {len(expected)} (einer pro übergebener " \
        f"Schwierigkeit, der Test übergibt {[d.name for d in expected]})."
    for d in expected:
        matching = [r for r in radios if d.name in r.cget("text")]
        assert matching, f"Kein Radiobutton mit {d.name!r} im Text. Kommen die Schwierigkeiten aus dem Parameter?"
        matching[0].invoke()
        assert menu.difficulty_choice.get() == d.name, \
            f"Klick auf {d.name!r} setzt difficulty_choice auf {menu.difficulty_choice.get()!r}, erwartet {d.name!r}."


def test_start_stores_selection(tk_root):
    """start_button speichert (UI-Name, DifficultyConfig) in selection und schließt das Fenster"""
    menu = _menu(tk_root)
    assert isinstance(getattr(menu, "start_button", None), tk.Button), "menu.start_button soll ein tk.Button sein."
    medium = _by_name("Medium")
    menu.ui_choice.set("Beta")
    menu.difficulty_choice.set(medium.name)
    menu.start_button.invoke()
    assert menu.selection is not None, "Nach Start ist selection noch None. Hängt _on_start am Button (command=…)?"
    ui, difficulty = menu.selection
    assert ui == "Beta"
    assert not isinstance(difficulty, str), \
        "selection[1] ist ein String. Gesucht ist das DifficultyConfig-Objekt aus difficulties, nicht nur sein Name."
    assert difficulty is medium, f"selection[1] ist {difficulty!r}, erwartet das Objekt {medium!r} aus difficulties."
    assert _destroyed(tk_root), \
        "Das Fenster ist nach Start noch offen. Schließ es mit self.master.destroy() (quit() beendet nur die " \
        "Schleife, das Fenster bliebe neben dem Spiel stehen)."


def test_run_returns_selection(tk_root):
    """run() zeigt das Menü, wartet auf Start und gibt die Auswahl zurück"""
    menu = _menu(tk_root)
    seen = {}

    def press_start():
        seen["manager"] = menu.winfo_manager()
        menu.ui_choice.set("Beta")
        try:
            menu.start_button.invoke()
        except Exception as e:   # Fehler in _on_start: melden statt auf den Timeout zu warten
            seen["error"] = f"{type(e).__name__}: {e}"
            tk_root.destroy()

    def give_up():
        seen["timeout"] = True
        tk_root.destroy()

    tk_root.after(50, press_start)
    guard = tk_root.after(3000, give_up)
    try:
        result = menu.run()
    finally:
        try:
            tk_root.after_cancel(guard)   # sonst feuert der Timer später in einem anderen Fenster
        except tk.TclError:
            pass
    assert "manager" in seen, "run() kehrt zurück, ohne zu warten. Fehlt self.master.mainloop()?"
    assert seen["manager"], "Das Menü ist nicht platziert, das Fenster bliebe leer. Fehlt self.pack() in run()?"
    assert "error" not in seen, f"Der Klick auf Start wirft einen Fehler in _on_start: {seen.get('error')}"
    assert "timeout" not in seen, "run() endet nach Start nicht. Schließt _on_start das Fenster?"
    expected = ("Beta", _menu_difficulties()[0])
    assert result == expected, f"run() gibt {result!r} zurück, erwartet die Auswahl aus selection: {expected!r}."


def test_run_closed_without_start(tk_root):
    """Fenster ohne Start schließen → run() gibt None zurück"""
    menu = _menu(tk_root)
    tk_root.after(50, tk_root.destroy)
    assert menu.run() is None


# ─────────────────────────────────────────────── __main__.py

def _import_main(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("beim Import")
    monkeypatch.setattr(tk, "Tk", boom)
    monkeypatch.setattr(curses, "wrapper", boom)
    sys.modules.pop("pysweeper.__main__", None)
    try:
        return importlib.import_module("pysweeper.__main__")
    except RuntimeError:
        pytest.fail("Beim bloßen Import öffnet __main__.py schon ein Fenster oder startet curses. "
                    "Das gehört unter if __name__ == \"__main__\":", pytrace=False)
    except Exception as e:
        pytest.fail(f"pysweeper/__main__.py lässt sich nicht importieren: {type(e).__name__}: {e}", pytrace=False)


def test_main_has_launchers(monkeypatch):
    """__main__.py hat LAUNCHERS = {"Terminal": …, "Tkinter": …} mit Startfunktionen(difficulty)"""
    mod = _import_main(monkeypatch)
    launchers = getattr(mod, "LAUNCHERS", None)
    assert isinstance(launchers, dict), "In __main__.py fehlt das dict LAUNCHERS (UI-Name → Startfunktion)."
    assert set(launchers) == {"Terminal", "Tkinter"}, f"LAUNCHERS hat die Schlüssel {sorted(launchers)}."
    for name, start in launchers.items():
        assert callable(start), f"LAUNCHERS[{name!r}] ist keine Funktion."
        signature = inspect.signature(start)
        try:
            signature.bind(object())
        except TypeError:
            pytest.fail(f"LAUNCHERS[{name!r}] hat die Signatur {signature}. Sie soll mit genau einem Argument "
                        f"aufrufbar sein: LAUNCHERS[{name!r}](difficulty).", pytrace=False)


class _FakeScreen:
    """Steht für stdscr, falls curses.wrapper durch den Fake die Startfunktion aufruft."""


def run_main(monkeypatch, selections):
    """Führt `python -m pysweeper` aus, mit einem Fake-StartMenu, das nacheinander `selections` liefert.

    Die echten UIs starten nicht: TerminalUI.run und TkinterUI.run merken sich nur das Spiel.
    """
    calls = {"menus": [], "terminal": [], "tkinter": [], "wrapper": 0}
    selections = list(selections)
    created = []
    real_tk = tk.Tk

    class TrackedTk(real_tk):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.withdraw()
            # Notbremse: Läuft doch das echte StartMenu, beendet das seine mainloop nach 2 s. quit() ist nötig,
            # weil mainloop() erst endet, wenn *alle* Tk-Fenster zu sind, und das Fenster aus tk_root noch offen ist.
            self.guard = self.after(2000, lambda: (self.quit(), self.destroy()))
            created.append(self)

    class FakeMenu:
        def __init__(self, master, ui_names, difficulties):
            try:
                master.winfo_exists()
            except (tk.TclError, AttributeError):
                pytest.fail("StartMenu bekommt als master kein offenes Fenster. Das Menü schließt sein Fenster "
                            "mit destroy(), deshalb braucht jede Runde ein neues tk.Tk().", pytrace=False)
            self.master = master
            calls["menus"].append((list(ui_names), list(difficulties)))

        def run(self):
            self.master.destroy()   # wie das echte Menü: nach der Auswahl ist das Fenster zu
            return selections.pop(0) if selections else None

    def fake_wrapper(func, *args, **kwargs):
        if not calls["menus"]:
            pytest.fail("curses.wrapper läuft, bevor das StartMenu gezeigt wurde. Ist das alte curses-Menü "
                        "(menu/choose) noch aktiv?", pytrace=False)
        calls["wrapper"] += 1
        return func(_FakeScreen(), *args, **kwargs)

    monkeypatch.setattr(need("pysweeper.ui.start_menu"), "StartMenu", FakeMenu)
    ui_package = need("pysweeper.ui")
    if hasattr(ui_package, "StartMenu"):   # falls StartMenu auch über pysweeper.ui importiert wird
        monkeypatch.setattr(ui_package, "StartMenu", FakeMenu)
    monkeypatch.setattr(need("pysweeper.ui.terminal_ui", "TerminalUI"), "run",
                        lambda self, game: calls["terminal"].append(game))
    monkeypatch.setattr(need("pysweeper.ui.tkinter_ui", "TkinterUI"), "run",
                        lambda self, game: calls["tkinter"].append(game))
    monkeypatch.setattr(curses, "wrapper", fake_wrapper)
    monkeypatch.setattr(tk, "Tk", TrackedTk)
    sys.modules.pop("pysweeper.__main__", None)
    try:
        runpy.run_module("pysweeper", run_name="__main__")
    except Exception as e:
        pytest.fail(f"python -m pysweeper bricht ab: {type(e).__name__}: {e}", pytrace=False)
    finally:
        for root in created:
            try:
                root.after_cancel(root.guard)
                root.destroy()
            except tk.TclError:
                pass   # schon geschlossen
    return calls


def _check_menu_args(calls):
    assert calls["menus"], \
        "python -m pysweeper zeigt kein StartMenu aus pysweeper/ui/start_menu.py. Wird es mit " \
        "`from pysweeper.ui.start_menu import StartMenu` importiert und StartMenu(...).run() aufgerufen?"
    ui_names, difficulties = calls["menus"][0]
    assert set(ui_names) == {"Terminal", "Tkinter"}, \
        f"StartMenu bekommt die UI-Namen {ui_names}. Gib ihm list(LAUNCHERS) mit."
    assert difficulties == _difficulties(), "StartMenu bekommt nicht DIFFICULTIES als Schwierigkeiten."


def test_main_starts_tkinter(monkeypatch, tk_root):
    """Auswahl („Tkinter“, Medium) startet TkinterUI mit Game(Medium), ohne curses"""
    medium = _by_name("Medium")
    calls = run_main(monkeypatch, [("Tkinter", medium)])
    _check_menu_args(calls)
    assert calls["wrapper"] == 0, \
        "curses.wrapper wurde aufgerufen, obwohl Tkinter gewählt wurde. Läuft noch das alte curses-Menü?"
    assert len(calls["tkinter"]) == 1 and not calls["terminal"], \
        f"Gestartet: {len(calls['tkinter'])}× Tkinter, {len(calls['terminal'])}× Terminal, erwartet 1× Tkinter."
    assert calls["tkinter"][0].difficulty == medium, "TkinterUI bekommt ein Game mit der falschen Schwierigkeit."


def test_main_starts_terminal(monkeypatch, tk_root):
    """Auswahl („Terminal“, Hard) startet TerminalUI per curses.wrapper mit Game(Hard)"""
    hard = _by_name("Hard")
    calls = run_main(monkeypatch, [("Terminal", hard)])
    _check_menu_args(calls)
    assert calls["wrapper"] == 1, f"curses.wrapper wurde {calls['wrapper']}× aufgerufen, erwartet 1× (nur fürs Spiel)."
    assert len(calls["terminal"]) == 1 and not calls["tkinter"], \
        f"Gestartet: {len(calls['terminal'])}× Terminal, {len(calls['tkinter'])}× Tkinter, erwartet 1× Terminal."
    assert calls["terminal"][0].difficulty == hard, "TerminalUI bekommt ein Game mit der falschen Schwierigkeit."


def test_main_menu_closed(monkeypatch, tk_root):
    """Menü ohne Start geschlossen → es startet kein Spiel"""
    calls = run_main(monkeypatch, [])
    _check_menu_args(calls)
    assert not calls["terminal"] and not calls["tkinter"] and calls["wrapper"] == 0, \
        "Obwohl das Menü ohne Auswahl geschlossen wurde (None), startet ein Spiel."
