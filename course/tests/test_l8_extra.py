"""L8+ – Nach jedem Spiel zurück ins Startmenü."""
from test_l8 import _by_name, run_main


def test_back_to_menu(monkeypatch, tk_root):
    """Menü → Tkinter-Spiel → Menü → Terminal-Spiel → Menü geschlossen: 2 Spiele, 3× Menü"""
    easy, medium = _by_name("Easy"), _by_name("Medium")
    calls = run_main(monkeypatch, [("Tkinter", easy), ("Terminal", medium)])
    assert len(calls["menus"]) == 3, \
        f"Das Startmenü kam {len(calls['menus'])}× statt 3×. Zeigst du es nach jedem Spiel erneut " \
        f"(Schleife, bis run() None liefert)?"
    assert [g.difficulty for g in calls["tkinter"]] == [easy]
    assert [g.difficulty for g in calls["terminal"]] == [medium]
