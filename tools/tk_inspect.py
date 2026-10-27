"""Startet das Tkinter-Spiel für das tkinter-mcp-Tool `launch_app`.

`launch_app` nimmt nur einen Skriptpfad und startet ihn ohne Terminal. Das curses-Menü aus
`python -m pysweeper` geht dort nicht, deshalb startet dieses Skript die Tkinter-UI direkt.
Optional: Schwierigkeit als Argument, z. B. `tools/tk_inspect.py Hard` (Standard: Easy).
"""
import pathlib
import sys
import tkinter as tk

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))   # Projektordner, damit `pysweeper` importierbar ist

from pysweeper.__main__ import run_tkinter   # noqa: E402  (enthält den Tcl-Fix für die venv)
from pysweeper.difficulty_config import DIFFICULTIES   # noqa: E402

_tk_init = tk.Tk.__init__   # schon von tkinter-mcp gepatcht (startet dessen Agent)


def _tk_init_on_top(self, *args, **kwargs):
    # view_application fotografiert nur den Bildschirmbereich des Fensters. Auf macOS bleibt ein so
    # gestartetes Fenster hinter der aktiven App, deshalb hier immer im Vordergrund halten.
    _tk_init(self, *args, **kwargs)
    self.after(200, lambda: (self.lift(), self.attributes("-topmost", True)))


tk.Tk.__init__ = _tk_init_on_top

try:
    # tkinter-mcp 0.9.3 nimmt Faktor 2 an, sobald *irgendein* Bildschirm „Retina“ ist (z. B. das MacBook-Display
    # neben einem externen Monitor), und schneidet dann falsch aus. Den echten Faktor messen: Pixel ÷ Punkte.
    import pyautogui
    from tkinter_mcp.introspection import screenshot as _mcp_screenshot

    _mcp_screenshot._dpi_scale_cache = pyautogui.screenshot().width / pyautogui.size().width
except ImportError:
    pass   # ohne tkinter-mcp gestartet: nichts zu korrigieren

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Easy"
    run_tkinter(next(d for d in DIFFICULTIES if d.name == name))
