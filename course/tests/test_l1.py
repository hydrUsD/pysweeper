"""L1 – GameState (Enum) und DifficultyConfig (dataclass)."""
import dataclasses
import enum

import pytest

from _helpers import need


def test_gamestate_is_enum():
    """GameState ist ein Enum"""
    GameState = need("pysweeper.game_state", "GameState")
    assert isinstance(GameState, type) and issubclass(GameState, enum.Enum), \
        "GameState soll von enum.Enum erben: class GameState(Enum): ..."


def test_gamestate_members():
    """GameState hat genau PLAYING, WON und LOST"""
    GameState = need("pysweeper.game_state", "GameState")
    names = {m.name for m in GameState}
    assert names == {"PLAYING", "WON", "LOST"}, f"Gefundene Mitglieder: {sorted(names)}"


def test_gamestate_identity():
    """GameState-Mitglieder sind Singletons (Vergleich mit `is`)"""
    GameState = need("pysweeper.game_state", "GameState")
    assert GameState["WON"] is GameState.WON
    assert GameState.WON is not GameState.LOST


def test_difficulty_is_dataclass():
    """DifficultyConfig ist eine dataclass mit den Feldern name, amount, size"""
    DifficultyConfig = need("pysweeper.difficulty_config", "DifficultyConfig")
    assert dataclasses.is_dataclass(DifficultyConfig), "Fehlt der Dekorator @dataclass?"
    fields = [f.name for f in dataclasses.fields(DifficultyConfig)]
    assert fields == ["name", "amount", "size"], \
        f"Felder in dieser Reihenfolge erwartet: name, amount, size. Gefunden: {fields}"


def test_difficulty_frozen():
    """DifficultyConfig ist unveränderlich (frozen)"""
    DifficultyConfig = need("pysweeper.difficulty_config", "DifficultyConfig")
    config = DifficultyConfig("Test", 1, (2, 3))
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.amount = 5
        pytest.fail("config.amount = 5 hat funktioniert. Fehlt frozen=True?", pytrace=False)


def test_difficulty_value_equality():
    """Zwei DifficultyConfigs mit gleichen Werten sind gleich (==)"""
    DifficultyConfig = need("pysweeper.difficulty_config", "DifficultyConfig")
    assert DifficultyConfig("A", 1, (2, 3)) == DifficultyConfig("A", 1, (2, 3))


@pytest.mark.parametrize("const, name, amount, size", [
    ("EASY", "Easy", 10, (9, 9)),
    ("MEDIUM", "Medium", 40, (16, 16)),
    ("HARD", "Hard", 99, (30, 16)),
], ids=["EASY", "MEDIUM", "HARD"])
def test_difficulty_constants(const, name, amount, size):
    """EASY / MEDIUM / HARD haben die Werte aus main.py, size als (width, height)"""
    DifficultyConfig = need("pysweeper.difficulty_config", "DifficultyConfig")
    value = need("pysweeper.difficulty_config", const)
    assert isinstance(value, DifficultyConfig), f"{const} soll ein DifficultyConfig-Objekt sein."
    if const == "HARD" and value.size == (16, 30):
        pytest.fail("HARD.size ist (16, 30). main.py speichert (rows, cols), das Diagramm will "
                    "(width, height). HARD ist 30 breit und 16 hoch.", pytrace=False)
    assert (value.name, value.amount, value.size) == (name, amount, size), \
        f"Erwartet {(name, amount, size)}, gefunden {(value.name, value.amount, value.size)}"


def test_difficulties_list():
    """DIFFICULTIES enthält EASY, MEDIUM, HARD in dieser Reihenfolge"""
    mod = need("pysweeper.difficulty_config")
    difficulties = need("pysweeper.difficulty_config", "DIFFICULTIES")
    assert list(difficulties) == [mod.EASY, mod.MEDIUM, mod.HARD]
