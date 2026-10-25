"""L5 – Game: der Controller."""
import pytest

from _helpers import make_board, need, revealed


@pytest.fixture
def mods():
    class M:
        Game = need("pysweeper.game", "Game")
        GameState = need("pysweeper.game_state", "GameState")
        Board = need("pysweeper.board", "Board")
        EASY = need("pysweeper.difficulty_config", "EASY")
        MEDIUM = need("pysweeper.difficulty_config", "MEDIUM")
        HARD = need("pysweeper.difficulty_config", "HARD")
    return M


def small_game(m):
    """Game mit festem 3x1-Brett: Mine links, zwei sichere Felder rechts."""
    game = m.Game(m.EASY)
    game.board = make_board(3, 1, {(0, 0)})
    return game


def test_init(mods):
    """Game(EASY): difficulty, state PLAYING und ein 9x9-Board mit 10 Minen"""
    game = mods.Game(mods.EASY)
    assert game.difficulty == mods.EASY
    assert game.state is mods.GameState.PLAYING, f"state ist {game.state!r}, erwartet GameState.PLAYING."
    assert isinstance(game.board, mods.Board), "game.board soll ein Board sein (Komposition)."
    assert (game.board.width, game.board.height, game.board.mine_amount) == (9, 9, 10)


def test_init_size_order(mods):
    """Game(HARD) baut ein Board mit width=30 und height=16"""
    game = mods.Game(mods.HARD)
    assert (game.board.width, game.board.height) == (30, 16), \
        f"Gefunden {game.board.width}x{game.board.height}. size ist (width, height)."


def test_reveal_delegates(mods):
    """game.reveal(x, y) deckt über das Board auf"""
    game = mods.Game(mods.EASY)
    game.reveal(2, 7)
    assert game.board.grid[7][2].is_revealed is True, "Nach game.reveal(2, 7) soll grid[7][2] offen sein."
    assert game.state is mods.GameState.PLAYING, "Der erste Klick ist immer sicher."


def test_lose(mods):
    """Aufdecken einer Mine führt zu LOST"""
    game = small_game(mods)
    game.reveal(0, 0)
    assert game.state is mods.GameState.LOST


def test_win(mods):
    """Alle sicheren Felder aufgedeckt führt zu WON"""
    game = small_game(mods)
    game.reveal(1, 0)
    assert game.state is mods.GameState.PLAYING
    game.reveal(2, 0)
    assert game.state is mods.GameState.WON


def test_no_moves_after_game_over(mods):
    """Nach Spielende werden reveal und toggle_flag ignoriert"""
    game = small_game(mods)
    game.reveal(0, 0)
    game.reveal(1, 0)
    game.toggle_flag(2, 0)
    assert (1, 0) not in revealed(game.board), "Nach LOST darf nichts mehr aufgedeckt werden."
    assert game.board.grid[0][2].is_flagged is False, "Nach LOST darf nichts mehr markiert werden."
    assert game.state is mods.GameState.LOST


def test_toggle_flag(mods):
    """game.toggle_flag(x, y) markiert über das Board"""
    game = mods.Game(mods.EASY)
    game.toggle_flag(4, 1)
    assert game.board.grid[1][4].is_flagged is True


def test_reveal_flagged_does_nothing(mods):
    """Eine markierte Mine aufdecken verliert nicht"""
    game = small_game(mods)
    game.toggle_flag(0, 0)
    game.reveal(0, 0)
    assert game.state is mods.GameState.PLAYING


def test_reset_board(mods):
    """reset_board(): neues Board, state wieder PLAYING, gleiche Schwierigkeit"""
    game = small_game(mods)
    game.reveal(0, 0)
    old_board = game.board
    game.reset_board()
    assert game.board is not old_board, "reset_board soll ein neues Board erzeugen."
    assert game.state is mods.GameState.PLAYING
    assert game.difficulty == mods.EASY
    assert (game.board.width, game.board.height) == (9, 9)


def test_set_difficulty(mods):
    """set_difficulty(MEDIUM): neue Schwierigkeit und passendes neues Board"""
    game = mods.Game(mods.EASY)
    game.reveal(4, 4)
    game.set_difficulty(mods.MEDIUM)
    assert game.difficulty == mods.MEDIUM
    assert (game.board.width, game.board.height, game.board.mine_amount) == (16, 16, 40)
    assert game.state is mods.GameState.PLAYING
    assert not revealed(game.board), "Nach set_difficulty soll ein frisches Board da sein."
