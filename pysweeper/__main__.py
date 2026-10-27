import curses
import os
import sys
from pathlib import Path

from pysweeper.difficulty_config import DIFFICULTIES, DifficultyConfig
from pysweeper.game import Game
from pysweeper.ui.terminal_ui import DOWN, SELECT, UP, TerminalUI

UIS = ["Terminal", "Tkinter"]


def _put(stdscr, y, x, text, attr=0):
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def choose(stdscr, title: str, options: list[str]) -> int | None:
    choice = 0
    while True:
        stdscr.erase()
        _put(stdscr, 0, 2, title, curses.A_BOLD)
        for i, option in enumerate(options):
            _put(stdscr, 2 + i, 4, option, curses.A_REVERSE if i == choice else 0)
        _put(stdscr, 3 + len(options), 2, "Up/Down choose  Enter select  Q quit", curses.A_DIM)
        stdscr.refresh()
        key = stdscr.getch()
        if key in UP:
            choice = (choice - 1) % len(options)
        elif key in DOWN:
            choice = (choice + 1) % len(options)
        elif key in SELECT:
            return choice
        elif key in (ord('q'), ord('Q')):
            return None


def menu(stdscr) -> tuple[str, DifficultyConfig] | None:
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.keypad(True)
    ui = choose(stdscr, "Minesweeper - choose UI", UIS)
    if ui is None:
        return None
    labels = [f"{d.name:<8}{d.size[0]:>2}x{d.size[1]:<2}  {d.amount:>3} mines" for d in DIFFICULTIES]
    difficulty = choose(stdscr, "Minesweeper - choose difficulty", labels)
    if difficulty is None:
        return None
    return UIS[ui], DIFFICULTIES[difficulty]


def run_terminal(stdscr, difficulty: DifficultyConfig) -> None:
    TerminalUI(stdscr).run(Game(difficulty))


def _use_base_tcl(tk) -> None:
    # In a venv, Tcl looks for its library next to the venv interpreter, so point it at the base install.
    lib = Path(sys.base_prefix) / "lib"
    for var, path in (("TCL_LIBRARY", lib / f"tcl{tk.TclVersion}"), ("TK_LIBRARY", lib / f"tk{tk.TkVersion}")):
        if var not in os.environ and path.is_dir():
            os.environ[var] = str(path)


def run_tkinter(difficulty: DifficultyConfig) -> None:
    import tkinter as tk

    from pysweeper.ui.tkinter_ui import TkinterUI

    _use_base_tcl(tk)
    root = tk.Tk()
    root.title(f"Minesweeper - {difficulty.name}")
    TkinterUI(root).run(Game(difficulty))


if __name__ == "__main__":
    selection = curses.wrapper(menu)
    if selection is not None:
        ui, difficulty = selection
        if ui == "Terminal":
            curses.wrapper(run_terminal, difficulty)
        else:
            run_tkinter(difficulty)
