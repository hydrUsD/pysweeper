import curses
import os
import tkinter as tk
import sys
from pathlib import Path

from pysweeper.difficulty_config import DIFFICULTIES, DifficultyConfig
from pysweeper.game import Game
from pysweeper.ui.start_menu import StartMenu
from pysweeper.ui.terminal_ui import TerminalUI

def run_terminal(stdscr, difficulty: DifficultyConfig) -> None:
    TerminalUI(stdscr).run(Game(difficulty))


def _use_base_tcl(tk) -> None:
    # In a venv, Tcl looks for its library next to the venv interpreter, so point it at the base install.
    lib = Path(sys.base_prefix) / "lib"
    for var, path in (("TCL_LIBRARY", lib / f"tcl{tk.TclVersion}"), ("TK_LIBRARY", lib / f"tk{tk.TkVersion}")):
        if var not in os.environ and path.is_dir():
            os.environ[var] = str(path)


def run_tkinter(difficulty: DifficultyConfig) -> None:
    from pysweeper.ui.tkinter_ui import TkinterUI

    _use_base_tcl(tk)
    root = tk.Tk()
    root.title(f"Minesweeper - {difficulty.name}")
    TkinterUI(root).run(Game(difficulty))


def start_terminal(difficulty: DifficultyConfig) -> None:
    curses.wrapper(run_terminal, difficulty)


LAUNCHERS = {"Terminal": start_terminal, "Tkinter": run_tkinter}


if __name__ == "__main__":
    _use_base_tcl(tk)
    while (selection := StartMenu(tk.Tk(), list(LAUNCHERS), DIFFICULTIES).run()) is not None:
        ui, difficulty = selection
        LAUNCHERS[ui](difficulty)
