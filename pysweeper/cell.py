class Cell:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0

    def toggle_flag(self) -> None:
        if self.is_revealed:
            return
        self.is_flagged = not self.is_flagged
