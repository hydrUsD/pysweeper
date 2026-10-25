"""Minesweeper in the terminal with curses.

Controls: arrow keys or WASD to move, Space/Enter to reveal, F to flag,
R to restart, M for the difficulty menu, Q to quit.
Revealing an already open number whose flags are all placed opens its
remaining neighbours ("chording").
"""
import curses
import time

import numpy as np

# Board sizes are (rows, cols), matching numpy's shape order.
EASY = {
    'name': 'Easy',
    'settings': {
        'amount': 10,
        'board': (9, 9)
    }
}
MEDIUM = {
    'name': 'Medium',
    'settings': {
        'amount': 40,
        'board': (16, 16)
    }
}
HARD = {
    'name': 'Hard',
    'settings': {
        'amount': 99,
        'board': (16, 30)
    }
}
DIFFICULTIES = [EASY, MEDIUM, HARD]


def new_board(difficulty):
    """Return an empty board. After mines are placed each cell holds
    '*' for a mine or '0'-'8' for the number of neighbouring mines."""
    return np.full(difficulty['settings']['board'], ' ', dtype='<U1')


# --------------------------------------------------------------------------
# Game logic
# --------------------------------------------------------------------------

class Game:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.rows, self.cols = difficulty['settings']['board']
        self.mine_count = difficulty['settings']['amount']
        self.board = new_board(difficulty)
        self.revealed = np.zeros((self.rows, self.cols), dtype=bool)
        self.flagged = np.zeros((self.rows, self.cols), dtype=bool)
        self.mines_placed = False
        self.state = 'playing'          # 'playing', 'won' or 'lost'
        self.start_time = None
        self.end_time = None
        self.cursor = [self.rows // 2, self.cols // 2]

    def neighbours(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def place_mines(self, safe_r, safe_c):
        """Place mines after the first reveal so the first cell (and its
        neighbours, if there is room) is always safe."""
        safe = {(safe_r, safe_c), *self.neighbours(safe_r, safe_c)}
        cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        candidates = [cell for cell in cells if cell not in safe]
        if len(candidates) < self.mine_count:
            candidates = [cell for cell in cells if cell != (safe_r, safe_c)]

        rng = np.random.default_rng()
        for i in rng.choice(len(candidates), self.mine_count, replace=False):
            self.board[candidates[i]] = '*'

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r, c] != '*':
                    count = sum(self.board[n] == '*' for n in self.neighbours(r, c))
                    self.board[r, c] = str(count)

        self.mines_placed = True
        self.start_time = time.monotonic()

    def reveal(self, r, c):
        if self.state != 'playing' or self.flagged[r, c]:
            return
        if not self.mines_placed:
            self.place_mines(r, c)
        if self.revealed[r, c]:
            self.chord(r, c)
            return
        if self.board[r, c] == '*':
            self.revealed[r, c] = True
            self.finish('lost')
            return

        # Flood-fill outward from empty cells.
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if self.revealed[cr, cc] or self.flagged[cr, cc]:
                continue
            self.revealed[cr, cc] = True
            if self.board[cr, cc] == '0':
                stack.extend(n for n in self.neighbours(cr, cc) if not self.revealed[n])
        self.check_win()

    def chord(self, r, c):
        value = self.board[r, c]
        if value in ('0', '*'):
            return
        around = list(self.neighbours(r, c))
        if sum(self.flagged[n] for n in around) != int(value):
            return
        for n in around:
            if not self.revealed[n] and not self.flagged[n]:
                self.reveal(*n)

    def toggle_flag(self, r, c):
        if self.state == 'playing' and not self.revealed[r, c]:
            self.flagged[r, c] = not self.flagged[r, c]

    def check_win(self):
        if self.state == 'playing' and self.revealed.sum() == self.rows * self.cols - self.mine_count:
            self.flagged[self.board == '*'] = True
            self.finish('won')

    def finish(self, state):
        self.state = state
        self.end_time = time.monotonic()

    @property
    def mines_left(self):
        return self.mine_count - int(self.flagged.sum())

    @property
    def elapsed(self):
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time is not None else time.monotonic()
        return int(end - self.start_time)

    def move(self, dr, dc):
        self.cursor[0] = min(max(self.cursor[0] + dr, 0), self.rows - 1)
        self.cursor[1] = min(max(self.cursor[1] + dc, 0), self.cols - 1)


# --------------------------------------------------------------------------
# Display
# --------------------------------------------------------------------------

FLAG_PAIR = 9
MINE_PAIR = 10
NUMBER_COLORS = {
    1: curses.COLOR_BLUE, 2: curses.COLOR_GREEN, 3: curses.COLOR_RED,
    4: curses.COLOR_MAGENTA, 5: curses.COLOR_YELLOW, 6: curses.COLOR_CYAN,
    7: curses.COLOR_WHITE, 8: curses.COLOR_WHITE,
}
HELP = 'Arrows/WASD move  Space reveal  F flag  R restart  M menu  Q quit'


def init_colors():
    if not curses.has_colors():
        return
    curses.start_color()
    try:
        curses.use_default_colors()
        background = -1
    except curses.error:
        background = curses.COLOR_BLACK
    for number, color in NUMBER_COLORS.items():
        curses.init_pair(number, color, background)
    curses.init_pair(FLAG_PAIR, curses.COLOR_RED, background)
    curses.init_pair(MINE_PAIR, curses.COLOR_WHITE, curses.COLOR_RED)


def pair(n):
    return curses.color_pair(n) if curses.has_colors() else 0


def put(win, y, x, text, attr=0):
    """addstr that ignores writes past the screen edge."""
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def cell_look(game, r, c):
    """Return (character, attribute) for one cell."""
    value = game.board[r, c]
    over = game.state != 'playing'
    if game.flagged[r, c]:
        if over and value != '*':
            return 'X', pair(FLAG_PAIR) | curses.A_BOLD   # wrong flag
        return 'F', pair(FLAG_PAIR) | curses.A_BOLD
    if game.revealed[r, c]:
        if value == '*':
            return '*', pair(MINE_PAIR) | curses.A_BOLD   # the mine you hit
        if value == '0':
            return ' ', 0
        return value, pair(int(value)) | curses.A_BOLD
    if game.state == 'lost' and value == '*':
        return '*', curses.A_BOLD
    return '.', curses.A_DIM


def draw(stdscr, game):
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    board_w = game.cols * 2 + 3
    need_h, need_w = game.rows + 6, max(board_w, len(HELP))

    if height < need_h or width < need_w:
        put(stdscr, 0, 0, f'Terminal too small: need {need_w}x{need_h}, '
                          f'have {width}x{height}.')
        put(stdscr, 1, 0, 'Resize the window, or press M for the menu / Q to quit.')
        stdscr.refresh()
        return

    left = (width - board_w) // 2
    top = 2

    title = f"Minesweeper - {game.difficulty['name']}"
    status = f'Mines: {game.mines_left:3d}   Time: {game.elapsed:3d}'
    put(stdscr, 0, left, title, curses.A_BOLD)
    put(stdscr, 0, max(left + board_w - len(status), left + len(title) + 2), status)

    # Border
    put(stdscr, top, left, '+' + '-' * (board_w - 2) + '+')
    for r in range(game.rows):
        put(stdscr, top + 1 + r, left, '|')
        put(stdscr, top + 1 + r, left + board_w - 1, '|')
    put(stdscr, top + game.rows + 1, left, '+' + '-' * (board_w - 2) + '+')

    # Cells, two columns wide each
    cur_r, cur_c = game.cursor
    for r in range(game.rows):
        for c in range(game.cols):
            ch, attr = cell_look(game, r, c)
            if (r, c) == (cur_r, cur_c):
                attr |= curses.A_REVERSE
            put(stdscr, top + 1 + r, left + 2 + c * 2, ch, attr)

    footer_y = top + game.rows + 3
    if game.state == 'won':
        put(stdscr, footer_y, left, f'You win! Cleared in {game.elapsed}s.',
            pair(2) | curses.A_BOLD)
        put(stdscr, footer_y + 1, left, 'R new game   M menu   Q quit')
    elif game.state == 'lost':
        put(stdscr, footer_y, left, 'Boom! You hit a mine.', pair(3) | curses.A_BOLD)
        put(stdscr, footer_y + 1, left, 'R new game   M menu   Q quit')
    else:
        put(stdscr, footer_y, (width - len(HELP)) // 2, HELP, curses.A_DIM)

    stdscr.refresh()


# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------

UP = (curses.KEY_UP, ord('w'), ord('W'))
DOWN = (curses.KEY_DOWN, ord('s'), ord('S'))
LEFT = (curses.KEY_LEFT, ord('a'), ord('A'))
RIGHT = (curses.KEY_RIGHT, ord('d'), ord('D'))
SELECT = (ord(' '), ord('\n'), curses.KEY_ENTER, 13)


def menu(stdscr):
    """Let the player pick a difficulty. Returns it, or None to quit."""
    stdscr.timeout(-1)
    choice = 0
    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        lines = ['MINESWEEPER', '']
        for d in DIFFICULTIES:
            rows, cols = d['settings']['board']
            lines.append(f"{d['name']:<8} {cols:>2}x{rows:<2}  {d['settings']['amount']:>3} mines")
        lines += ['', 'Up/Down choose   Enter start   Q quit']

        top = max((height - len(lines)) // 2, 0)
        for i, line in enumerate(lines):
            attr = curses.A_BOLD if i == 0 else 0
            if 2 <= i < 2 + len(DIFFICULTIES) and i - 2 == choice:
                attr |= curses.A_REVERSE
            put(stdscr, top + i, max((width - len(line)) // 2, 0), line, attr)
        stdscr.refresh()

        key = stdscr.getch()
        if key in UP:
            choice = (choice - 1) % len(DIFFICULTIES)
        elif key in DOWN:
            choice = (choice + 1) % len(DIFFICULTIES)
        elif key in SELECT:
            return DIFFICULTIES[choice]
        elif key in (ord('q'), ord('Q')):
            return None


def play(stdscr, difficulty):
    """Run one difficulty until the player quits ('quit') or goes to the menu ('menu')."""
    stdscr.timeout(250)   # wake up regularly so the timer keeps ticking
    game = Game(difficulty)
    while True:
        draw(stdscr, game)
        key = stdscr.getch()
        if key == -1 or key == curses.KEY_RESIZE:
            continue
        if key in (ord('q'), ord('Q')):
            return 'quit'
        if key in (ord('m'), ord('M')):
            return 'menu'
        if key in (ord('r'), ord('R')):
            game = Game(difficulty)
        elif key in UP:
            game.move(-1, 0)
        elif key in DOWN:
            game.move(1, 0)
        elif key in LEFT:
            game.move(0, -1)
        elif key in RIGHT:
            game.move(0, 1)
        elif key in SELECT:
            game.reveal(*game.cursor)
        elif key in (ord('f'), ord('F')):
            game.toggle_flag(*game.cursor)


def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.keypad(True)
    init_colors()

    while True:
        difficulty = menu(stdscr)
        if difficulty is None or play(stdscr, difficulty) == 'quit':
            return


if __name__ == '__main__':
    curses.wrapper(main)
