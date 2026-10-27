import curses

from pysweeper.difficulty_config import EASY
from pysweeper.game import Game
from pysweeper.ui.terminal_ui import TerminalUI


def main(stdscr):
    TerminalUI(stdscr).run(Game(EASY))


if __name__ == "__main__":
    curses.wrapper(main)
