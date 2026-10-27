from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pysweeper.board import Board
    from pysweeper.game import Game


class UserInterface(ABC):
    @abstractmethod
    def run(self, game: Game) -> None: ...

    @abstractmethod
    def draw_board(self, board: Board) -> None: ...
