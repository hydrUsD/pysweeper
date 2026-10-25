from enum import Enum, auto

class GameState(Enum):
    PLAYING = auto()
    WON = auto()
    LOST = auto()