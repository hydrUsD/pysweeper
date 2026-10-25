"""L5 Erweiterung – mines_left, Timer (elapsed) und Verlust durch Chording."""
import inspect
import time

import pytest

from _helpers import cells, make_board, need


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(time, "monotonic", fake)
    return fake


@pytest.fixture
def mods():
    class M:
        Game = need("pysweeper.game", "Game")
        GameState = need("pysweeper.game_state", "GameState")
        EASY = need("pysweeper.difficulty_config", "EASY")
    return M


def test_mines_left(mods):
    """mines_left ist eine Property: Minen minus gesetzte Flaggen"""
    assert isinstance(inspect.getattr_static(mods.Game, "mines_left", None), property), \
        "mines_left soll mit @property definiert sein."
    game = mods.Game(mods.EASY)
    assert game.mines_left == 10
    game.toggle_flag(0, 0)
    game.toggle_flag(1, 0)
    assert game.mines_left == 8


def test_elapsed_property(mods):
    """elapsed ist eine Property"""
    assert isinstance(inspect.getattr_static(mods.Game, "elapsed", None), property), \
        "elapsed soll mit @property definiert sein."


def test_elapsed_starts_at_first_reveal(mods, clock):
    """Der Timer startet erst beim ersten Aufdecken"""
    game = mods.Game(mods.EASY)
    clock.now += 50
    assert game.elapsed == 0, "Vor dem ersten Aufdecken soll elapsed 0 sein."
    game.reveal(4, 4)
    clock.now += 3.7
    assert game.elapsed == 3, (f"elapsed ist {game.elapsed!r}, erwartet 3 (ganze Sekunden seit dem "
                               f"ersten Aufdecken). Nutzt du time.monotonic() über `import time`?")


def test_elapsed_stops_at_game_over(mods, clock):
    """Der Timer bleibt bei Spielende stehen"""
    game = mods.Game(mods.EASY)
    game.reveal(4, 4)
    clock.now += 7
    x, y = next((c.x, c.y) for c in cells(game.board) if c.is_mine)
    game.reveal(x, y)
    clock.now += 100
    assert game.state is mods.GameState.LOST
    assert game.elapsed == 7, (f"elapsed ist {game.elapsed!r}, erwartet 7: Der Timer soll bei LOST anhalten. "
                               f"Setzt du end_time beim Spielende, und nutzt du time.monotonic() über "
                               f"`import time`?")


def test_reset_resets_timer(mods, clock):
    """reset_board setzt den Timer zurück"""
    game = mods.Game(mods.EASY)
    game.reveal(4, 4)
    clock.now += 20
    game.reset_board()
    assert game.elapsed == 0


def test_lose_by_chord(mods):
    """Verlust durch Chording mit falscher Flagge wird erkannt"""
    game = mods.Game(mods.EASY)
    game.board = make_board(3, 3, {(0, 0)})
    game.reveal(1, 1)
    game.toggle_flag(2, 2)
    game.reveal(1, 1)
    assert game.state is mods.GameState.LOST, ("Chording hat die Mine (0, 0) aufgedeckt, nicht die "
                                               "angeklickte Zelle. Nutze board.mine_revealed().")
