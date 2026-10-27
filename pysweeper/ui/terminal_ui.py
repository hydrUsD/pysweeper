from __future__ import annotations

import curses
from typing import TYPE_CHECKING

from pysweeper.game_state import GameState
from pysweeper.ui.user_interface import UserInterface

if TYPE_CHECKING:
    from pysweeper.board import Board
    from pysweeper.game import Game

FLAG_PAIR, MINE_PAIR = 9, 10
NUMBER_COLORS = {1: curses.COLOR_BLUE, 2: curses.COLOR_GREEN, 3: curses.COLOR_RED, 4: curses.COLOR_MAGENTA,
                 5: curses.COLOR_YELLOW, 6: curses.COLOR_CYAN, 7: curses.COLOR_WHITE, 8: curses.COLOR_WHITE}
HELP = 'Arrows/WASD move  Space reveal  F flag  R restart  Q quit'
UP = (curses.KEY_UP, ord('w'), ord('W'))
DOWN = (curses.KEY_DOWN, ord('s'), ord('S'))
LEFT = (curses.KEY_LEFT, ord('a'), ord('A'))
RIGHT = (curses.KEY_RIGHT, ord('d'), ord('D'))
SELECT = (ord(' '), ord('\n'), curses.KEY_ENTER, 13)


def _pair(n):
    return curses.color_pair(n) if curses.has_colors() else 0


class TerminalUI(UserInterface):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.cursor_x = 0
        self.cursor_y = 0
        self.game: Game | None = None

    def _setup_curses(self) -> None:
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self.stdscr.keypad(True)
        self.stdscr.timeout(250)
        if curses.has_colors():
            curses.start_color()
            try:
                curses.use_default_colors()
                bg = -1
            except curses.error:
                bg = curses.COLOR_BLACK
            for number, color in NUMBER_COLORS.items():
                curses.init_pair(number, color, bg)
            curses.init_pair(FLAG_PAIR, curses.COLOR_RED, bg)
            curses.init_pair(MINE_PAIR, curses.COLOR_WHITE, curses.COLOR_RED)

    def run(self, game: Game) -> None:
        self.game = game
        self._setup_curses()
        self.cursor_x, self.cursor_y = game.board.width // 2, game.board.height // 2
        while True:
            self.draw_board(self.game.board)
            key = self._get_input()
            if key in (-1, curses.KEY_RESIZE):
                continue
            if key in (ord('q'), ord('Q')):
                return
            if key in (ord('r'), ord('R')):
                self.game.reset_board()
            elif key in UP:
                self._move_cursor(0, -1)
            elif key in DOWN:
                self._move_cursor(0, 1)
            elif key in LEFT:
                self._move_cursor(-1, 0)
            elif key in RIGHT:
                self._move_cursor(1, 0)
            elif key in SELECT:
                self.game.reveal(self.cursor_x, self.cursor_y)
            elif key in (ord('f'), ord('F')):
                self.game.toggle_flag(self.cursor_x, self.cursor_y)

    def _get_input(self) -> int:
        return self.stdscr.getch()

    def _move_cursor(self, dx: int, dy: int) -> None:
        board = self.game.board
        self.cursor_x = min(max(self.cursor_x + dx, 0), board.width - 1)
        self.cursor_y = min(max(self.cursor_y + dy, 0), board.height - 1)

    def _put(self, y, x, text, attr=0):
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    def _cell_look(self, cell):
        if cell.is_flagged:
            return 'F', _pair(FLAG_PAIR) | curses.A_BOLD
        if cell.is_revealed:
            if cell.is_mine:
                return '*', _pair(MINE_PAIR) | curses.A_BOLD
            if cell.neighbor_mines == 0:
                return ' ', 0
            return str(cell.neighbor_mines), _pair(cell.neighbor_mines) | curses.A_BOLD
        return '.', curses.A_DIM

    def draw_board(self, board: Board) -> None:
        s = self.stdscr
        s.erase()
        left, top = 2, 2
        self._put(0, left, f"Minesweeper - {self.game.difficulty.name}", curses.A_BOLD)
        self._put(1, left, f'Mines: {self.game.mines_left:3d}   Time: {self.game.elapsed:3d}')
        for row in board.grid:
            for cell in row:
                ch, attr = self._cell_look(cell)
                if (cell.x, cell.y) == (self.cursor_x, self.cursor_y):
                    attr |= curses.A_REVERSE
                self._put(top + 1 + cell.y, left + 2 + cell.x * 2, ch, attr)
        footer = top + board.height + 3
        if self.game.state is GameState.WON:
            self._put(footer, left, f'You win! Cleared in {self.game.elapsed}s.')
        elif self.game.state is GameState.LOST:
            self._put(footer, left, 'Boom! You hit a mine.')
            self._put(footer + 1, left, 'R restart  Q quit', curses.A_DIM)
        else:
            self._put(footer, left, HELP, curses.A_DIM)
        s.refresh()
