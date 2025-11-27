# components.py
import random
import config

class CellState:
    def __init__(self, ismine=False, isrevealed=False, isflagged=False, adjacent=0):
        self.is_mine = ismine
        self.is_revealed = isrevealed
        self.is_flagged = isflagged
        self.adjacent_mines = adjacent

class Board:
    def __init__(self, cols, rows, num_mines):
        self.cols = cols
        self.rows = rows
        self.num_mines = num_mines
        self.game_over = False
        self.game_win = False
        self._mines_placed = False
        self.cells = [CellState() for _ in range(cols * rows)]

    def index(self, col, row):
        return row * self.cols + col

    def is_inbounds(self, col, row):
        return 0 <= col < self.cols and 0 <= row < self.rows

    def neighbors(self, col, row):
        neighbor_list = []
        for dcol in [-1, 0, 1]:
            for drow in [-1, 0, 1]:
                if dcol == 0 and drow == 0:
                    continue
                n_col, n_row = col + dcol, row + drow
                if self.is_inbounds(n_col, n_row):
                    neighbor_list.append((n_col, n_row))
        return neighbor_list

    def placemines(self, safecol, saferow):
        if self._mines_placed:
            return

        safe_indices = [self.index(safecol, saferow)]
        for n_col, n_row in self.neighbors(safecol, saferow):
            safe_indices.append(self.index(n_col, n_row))

        available_indices = [i for i in range(len(self.cells)) if i not in safe_indices]
        
        if len(available_indices) < self.num_mines:
             mines_to_place = len(available_indices)
        else:
             mines_to_place = self.num_mines

        mine_indices = random.sample(available_indices, mines_to_place)

        for i in mine_indices:
            self.cells[i].is_mine = True

        for row in range(self.rows):
            for col in range(self.cols):
                if not self.cells[self.index(col, row)].is_mine:
                    mine_count = 0
                    for n_col, n_row in self.neighbors(col, row):
                        if self.cells[self.index(n_col, n_row)].is_mine:
                            mine_count += 1
                    self.cells[self.index(col, row)].adjacent_mines = mine_count

        self._mines_placed = True

    def reveal(self, col, row):
        if not self.is_inbounds(col, row):
            return
        
        cell_index = self.index(col, row)
        cell = self.cells[cell_index]

        if cell.is_revealed or cell.is_flagged:
            return

        if not self._mines_placed:
            self.placemines(col, row)

        cell.is_revealed = True

        if cell.is_mine:
            self.game_over = True
            self._reveal_all_mines()
            return

        if cell.adjacent_mines == 0:
            for n_col, n_row in self.neighbors(col, row):
                self.reveal(n_col, n_row)

        self._check_win()

    def toggleflag(self, col, row):
        if not self.is_inbounds(col, row):
            return
        
        cell = self.cells[self.index(col, row)]
        
        if not cell.is_revealed:
            cell.is_flagged = not cell.is_flagged

    def flaggedcount(self):
        count = 0
        for cell in self.cells:
            if cell.is_flagged:
                count += 1
        return count

    def _reveal_all_mines(self):
        for cell in self.cells:
            if cell.is_mine:
                cell.is_revealed = True

    def _check_win(self):
        unrevealed_non_mines = 0
        for cell in self.cells:
            if not cell.is_mine and not cell.is_revealed:
                unrevealed_non_mines += 1
        
        if unrevealed_non_mines == 0 and self._mines_placed:
            self.game_win = True
            self.game_over = True # End game on win