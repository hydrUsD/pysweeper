"""L9+ – Falsch gesetzte Flaggen nach einer Niederlage als „X“ zeigen."""
import pytest

from _helpers import make_board, need


def _lost_game():
    """3×3-Brett, Minen auf (2, 0) und (2, 2). Flagge richtig auf (2, 0), falsch auf (0, 0), dann Mine (2, 2)."""
    Game = need("pysweeper.game", "Game")
    EASY = need("pysweeper.difficulty_config", "EASY")
    game = Game(EASY)
    game.board = make_board(3, 3, {(2, 0), (2, 2)})
    game.toggle_flag(2, 0)
    game.toggle_flag(0, 0)
    return game


def _ui(game):
    try:
        ui = need("pysweeper.ui.tkinter_ui", "TkinterUI")(None)
    except Exception as e:
        pytest.fail(f"TkinterUI(None) scheitert: {type(e).__name__}: {e}. Die Checks bauen TkinterUI(None): "
                    f"__init__ soll root nur speichern.", pytrace=False)
    ui.game = game
    if not callable(getattr(ui, "_cell_style", None)):
        pytest.fail("TkinterUI hat noch keine Methode _cell_style(cell). Erst Lektion 9 lösen.", pytrace=False)
    return ui


def test_no_x_while_playing():
    """Während des Spiels zeigt jede Flagge „F“, auch eine falsche"""
    game = _lost_game()
    ui = _ui(game)
    assert ui._cell_style(game.board.grid[0][0])["text"] == "F", \
        "Vor dem Spielende darf eine falsche Flagge nicht verraten werden."


def test_wrong_flag_after_loss():
    """Nach der Niederlage: falsche Flagge „X“, richtige Flagge weiter „F“"""
    game = _lost_game()
    game.reveal(2, 2)
    LOST = need("pysweeper.game_state", "GameState").LOST
    assert game.state is LOST, "Testaufbau: Das Spiel sollte nach dem Klick auf die Mine verloren sein."
    ui = _ui(game)
    wrong = ui._cell_style(game.board.grid[0][0])["text"]
    right = ui._cell_style(game.board.grid[0][2])["text"]
    assert wrong == "X", f"Die Flagge auf (0, 0) lag auf keiner Mine. Nach der Niederlage zeigt sie {wrong!r}, erwartet 'X'."
    assert right == "F", f"Die Flagge auf (2, 0) lag richtig. Sie zeigt {right!r}, erwartet weiter 'F'."
