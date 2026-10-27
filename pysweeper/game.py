import time

from pysweeper.board import Board
from pysweeper.difficulty_config import DifficultyConfig
from pysweeper.game_state import GameState


class Game:
    def __init__(self, difficulty: DifficultyConfig):
        self.difficulty = difficulty
        self.reset_board()

    def reset_board(self) -> None:
        width, height = self.difficulty.size
        self.board = Board(width, height, self.difficulty.amount)
        self.state = GameState.PLAYING
        self.start_time = None
        self.end_time = None

    def set_difficulty(self, new_difficulty: DifficultyConfig) -> None:
        self.difficulty = new_difficulty
        self.reset_board()

    def reveal(self, x: int, y: int) -> None:
        if self.state is not GameState.PLAYING:
            return
        if self.board.reveal_cell(x, y):
            if self.start_time is None:
                self.start_time = time.monotonic()
            if self.board.mine_revealed():
                self.board.reveal_mines()
                self._finish(GameState.LOST)
            elif self.board.check_win():
                self._finish(GameState.WON)

    def toggle_flag(self, x: int, y: int) -> None:
        if self.state is GameState.PLAYING:
            self.board.toggle_flag(x, y)

    def _finish(self, state):
        self.state = state
        self.end_time = time.monotonic()

    @property
    def mines_left(self) -> int:
        return self.board.mine_amount - self.board.flags_placed

    @property
    def elapsed(self) -> int:
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time is not None else time.monotonic()
        return int(end - self.start_time)
