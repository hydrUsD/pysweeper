import random

from pysweeper.cell import Cell


class Board:
    def __init__(self, width: int, height: int, mine_amount: int):
        self.width = width
        self.height = height
        self.mine_amount = mine_amount
        self.mines_planted = False
        self._initialize_board()

    def _initialize_board(self) -> None:
        self.grid = [[Cell(x, y) for x in range(self.width)] for y in range(self.height)]

    def _neighbors(self, x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    yield nx, ny

    def _plant_mines(self, safe_x: int, safe_y: int) -> None:
        safe = {(safe_x, safe_y), *self._neighbors(safe_x, safe_y)}
        positions = [(x, y) for y in range(self.height) for x in range(self.width)]
        candidates = [p for p in positions if p not in safe]
        if len(candidates) < self.mine_amount:
            candidates = [p for p in positions if p != (safe_x, safe_y)]
        for x, y in random.sample(candidates, self.mine_amount):
            self.grid[y][x].is_mine = True
        self.mines_planted = True

    def _calculate_neighbors(self) -> None:
        for row in self.grid:
            for cell in row:
                if not cell.is_mine:
                    cell.neighbor_mines = sum(self.grid[ny][nx].is_mine for nx, ny in self._neighbors(cell.x, cell.y))

    def reveal_cell(self, x: int, y: int) -> bool:
        cell = self.grid[y][x]
        if cell.is_flagged:
            return False
        if cell.is_revealed:
            return self._chord(x, y)
        if not self.mines_planted:
            self._plant_mines(x, y)
            self._calculate_neighbors()
        self._cascade_reveal(x, y)
        return True

    def _cascade_reveal(self, x: int, y: int) -> None:
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            cell = self.grid[cy][cx]
            if cell.is_revealed or cell.is_flagged:
                continue
            cell.is_revealed = True
            if not cell.is_mine and cell.neighbor_mines == 0:
                stack.extend(self._neighbors(cx, cy))

    def _chord(self, x, y) -> bool:
        cell = self.grid[y][x]
        if cell.is_mine or cell.neighbor_mines == 0:
            return False
        around = list(self._neighbors(x, y))
        if sum(self.grid[ny][nx].is_flagged for nx, ny in around) != cell.neighbor_mines:
            return False
        changed = False
        for nx, ny in around:
            n = self.grid[ny][nx]
            if not n.is_revealed and not n.is_flagged:
                self._cascade_reveal(nx, ny)
                changed = True
        return changed

    def toggle_flag(self, x: int, y: int) -> None:
        self.grid[y][x].toggle_flag()

    def check_win(self) -> bool:
        return all(c.is_revealed for row in self.grid for c in row if not c.is_mine)

    @property
    def flags_placed(self) -> int:
        return sum(c.is_flagged for row in self.grid for c in row)

    def mine_revealed(self) -> bool:
        return any(c.is_mine and c.is_revealed for row in self.grid for c in row)
