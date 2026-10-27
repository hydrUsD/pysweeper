import tkinter as tk

from pysweeper.game_state import GameState
from pysweeper.ui.user_interface import UserInterface


class TkinterUI(UserInterface):
    def __init__(self, root: tk.Tk):
        self.root = root
        self.buttons = []
        self.status = None
        self.game = None

    def _create_widgets(self, width: int, height: int) -> None:
        for y in range(height):
            row = []
            for x in range(width):
                b = tk.Button(self.root, width=2, command=lambda x=x, y=y: self._on_left_click(x, y))
                for event in ("<Button-2>", "<Button-3>"):
                    b.bind(event, lambda e, x=x, y=y: self._on_right_click(x, y))
                b.grid(row=y, column=x)
                row.append(b)
            self.buttons.append(row)
        self.status = tk.Label(self.root)
        self.status.grid(row=height, column=0, columnspan=width)

    def run(self, game) -> None:
        self.game = game
        self._create_widgets(game.board.width, game.board.height)
        self.draw_board(game.board)
        self.root.mainloop()

    def draw_board(self, board) -> None:
        for row in board.grid:
            for c in row:
                text = "F" if c.is_flagged else "" if not c.is_revealed else "*" if c.is_mine else str(c.neighbor_mines or "")
                self.buttons[c.y][c.x].config(text=text)
        self.status.config(text=self._status_text())

    def _status_text(self) -> str:
        if self.game.state is GameState.WON:
            return f"You win! Cleared in {self.game.elapsed}s."
        if self.game.state is GameState.LOST:
            return "Boom! You hit a mine."
        return ""

    def _on_left_click(self, x: int, y: int) -> None:
        self.game.reveal(x, y)
        self.draw_board(self.game.board)

    def _on_right_click(self, x: int, y: int) -> None:
        self.game.toggle_flag(x, y)
        self.draw_board(self.game.board)
