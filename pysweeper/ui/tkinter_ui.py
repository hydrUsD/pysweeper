import tkinter as tk

from pysweeper.game_state import GameState
from pysweeper.ui.user_interface import UserInterface

HELP = 'R restart  Q quit'
NUMBER_COLORS = {1: "#1f5fd1", 2: "#1a7f37", 3: "#cf222e", 4: "#6e40c9", 5: "#9a6700", 6: "#0a7f8c", 7: "#24292f", 8: "#57606a"}
CLOSED = {"relief": "raised", "bg": "#9a9a9a", "fg": "black", "text": ""}
OPEN = {"relief": "flat", "bg": "#e8e8e8", "fg": "black", "text": ""}


class TkinterUI(UserInterface):
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cells = []
        self.status = None
        self.game = None

    def _create_widgets(self, width: int, height: int) -> None:
        for y in range(height):
            row = []
            for x in range(width):
                label = tk.Label(self.root, width=2, bd=1)
                label.bind("<Button-1>", lambda e, x=x, y=y: self._on_left_click(x, y))
                for event in ("<Button-2>", "<Button-3>"):
                    label.bind(event, lambda e, x=x, y=y: self._on_right_click(x, y))
                label.grid(row=y, column=x, padx=1, pady=1)
                row.append(label)
            self.cells.append(row)
        self.status = tk.Label(self.root)
        self.status.grid(row=height, column=0, columnspan=width)
        for key in ("r", "R"):
            self.root.bind(f"<{key}>", lambda e: self._restart())
        for key in ("q", "Q"):
            self.root.bind(f"<{key}>", lambda e: self.root.destroy())

    def run(self, game) -> None:
        self.game = game
        self._create_widgets(game.board.width, game.board.height)
        self.draw_board(game.board)
        self.root.mainloop()

    def _cell_style(self, cell) -> dict:
        if cell.is_flagged:
            wrong = self.game.state is GameState.LOST and not cell.is_mine
            return {**CLOSED, "text": "X" if wrong else "F", "fg": "#cf222e"}
        if not cell.is_revealed:
            return CLOSED
        if cell.is_mine:
            return {**OPEN, "text": "*", "bg": "#ff8182"}
        if cell.neighbor_mines:
            return {**OPEN, "text": str(cell.neighbor_mines), "fg": NUMBER_COLORS[cell.neighbor_mines]}
        return OPEN

    def draw_board(self, board) -> None:
        for row in board.grid:
            for c in row:
                self.cells[c.y][c.x].config(**self._cell_style(c))
        self.status.config(text=self._status_text())

    def _status_text(self) -> str:
        if self.game.state is GameState.WON:
            return f"You win! Cleared in {self.game.elapsed}s.\n{HELP}"
        if self.game.state is GameState.LOST:
            return f"Boom! You hit a mine.\n{HELP}"
        return HELP

    def _restart(self) -> None:
        self.game.reset_board()
        self.draw_board(self.game.board)

    def _on_left_click(self, x: int, y: int) -> None:
        self.game.reveal(x, y)
        self.draw_board(self.game.board)

    def _on_right_click(self, x: int, y: int) -> None:
        self.game.toggle_flag(x, y)
        self.draw_board(self.game.board)
