from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyConfig:
    name: str
    amount: int
    size: tuple[int, int]


EASY = DifficultyConfig("Easy", 10, (9, 9))
MEDIUM = DifficultyConfig("Medium", 40, (16, 16))
HARD = DifficultyConfig("Hard", 99, (30, 16))
DIFFICULTIES = [EASY, MEDIUM, HARD]
