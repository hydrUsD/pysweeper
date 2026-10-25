from dataclasses import dataclass

@dataclass(frozen=True)
class DifficultyConfig:
    name: str
    amount: int
    size: tuple[int, int]

EASY: DifficultyConfig = DifficultyConfig(name="Easy", amount=10, size=(9, 9))
MEDIUM: DifficultyConfig = DifficultyConfig(name="Medium", amount=40, size=(16, 16))
HARD: DifficultyConfig = DifficultyConfig(name="Hard", amount=99, size=(30, 16))

DIFFICULTIES: list[DifficultyConfig] = [ EASY, MEDIUM, HARD ]