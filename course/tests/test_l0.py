"""L0 – Paketstruktur anlegen."""
import pytest

from _helpers import need

MODULES = [
    "pysweeper/game_state.py",
    "pysweeper/difficulty_config.py",
    "pysweeper/cell.py",
    "pysweeper/board.py",
    "pysweeper/game.py",
    "pysweeper/ui/user_interface.py",
    "pysweeper/ui/terminal_ui.py",
]


@pytest.fixture
def root(request):
    return request.config.rootpath


def test_package(root):
    """pysweeper/ ist ein Paket (mit __init__.py)"""
    assert (root / "pysweeper").is_dir(), "Es gibt noch keinen Ordner pysweeper/ neben main.py."
    assert (root / "pysweeper" / "__init__.py").is_file(), \
        "pysweeper/ braucht eine (leere) Datei __init__.py, erst dann ist es ein Paket."
    need("pysweeper")


def test_ui_package(root):
    """pysweeper/ui/ ist ein Unterpaket (mit __init__.py)"""
    assert (root / "pysweeper" / "ui" / "__init__.py").is_file(), \
        "pysweeper/ui/ braucht ebenfalls eine __init__.py."
    need("pysweeper.ui")


@pytest.mark.parametrize("path", MODULES)
def test_module_file(root, path):
    """Moduldatei existiert"""
    assert (root / path).is_file(), f"{path} fehlt noch."


def test_main_untouched(root):
    """main.py ist noch da (bleibt als Referenz unverändert)"""
    assert (root / "main.py").is_file(), "main.py ist verschwunden. Die brauchst du noch als Vorlage!"
