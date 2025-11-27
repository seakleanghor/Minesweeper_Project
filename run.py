# run.py
import pygame
import time
from components import Board, CellState
import config

class Renderer:
    """Handles drawing the game screen, header, and cell contents."""
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
    
    def draw_cell(self, col, row, cell):
        """Draws a single cell based on its state."""
        x = col * config.CELL_SIZE
        y = row * config.CELL_SIZE + 50 # Offset for header

        rect = pygame.Rect(x + config.CELL_BORDER, y + config.CELL_BORDER,
                           config.CELL_SIZE - 2 * config.CELL_BORDER, 
                           config.CELL_SIZE - 2 * config.CELL_BORDER)

        # Draw base color
        if cell.is_revealed:
            color = config.COLOR_CELL_REVEALED
        else:
            color = config.COLOR_CELL_UNREVEALED
        
        pygame.draw.rect(self.screen, color, rect)

        # Draw content
        if cell.is_revealed:
            if cell.is_mine:
                # Draw Mine (Red circle/X)
                pygame.draw.circle(self.screen, config.COLOR_RED, rect.center, config.CELL_SIZE // 3)
            elif cell.adjacent_mines > 0:
                # Draw number
                text = self.font.render(str(cell.adjacent_mines), True, config.NUM_COLORS.get(cell.adjacent_mines, config.COLOR_BLACK))
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)
        elif cell.is_flagged:
            # Draw Flag (Yellow/Green triangle)
            # Simple representation: a yellow 'F'
            text = self.font.render('F', True, config.COLOR_GREEN)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def draw_highlight(self, col, row):
        """Draws a highlight border around a cell."""
        x = col * config.CELL_SIZE
        y = row * config.CELL_SIZE + 50
        
        rect = pygame.Rect(x, y, config.CELL_SIZE, config.CELL_SIZE)
        pygame.draw.rect(self.screen, config.COLOR_HIGHLIGHT, rect, 2)

    def draw_header(self, board, elapsed_time):
        """Draws the status bar: Mines count and Time."""
        header_rect = pygame.Rect(0, 0, config.WINDOW_WIDTH, 50)
        pygame.draw.rect(self.screen, config.COLOR_GREY_LIGHT, header_rect)
        pygame.draw.line(self.screen, config.COLOR_BLACK, (0, 49), (config.WINDOW_WIDTH, 49), 2)
        
        # Display Mines: Total - Flagged
        mines_display = f"Mines: {board.num_mines - board.flaggedcount()}"
        mine_text = self.font.render(mines_display, True, config.COLOR_BLACK)
        self.screen.blit(mine_text, (10, 15))

        # Display Time
        time_display = f"Time: {int(elapsed_time):02d}"
        time_text = self.font.render(time_display, True, config.COLOR_BLACK)
        self.screen.blit(time_text, (config.WINDOW_WIDTH - time_text.get_width() - 10, 15))

    def draw_game_state_message(self, board):
        """Draws Game Over or Win message."""
        if board.game_over:
            message = "YOU WIN!" if board.game_win else "GAME OVER"
            color = config.COLOR_GREEN if board.game_win else config.COLOR_RED
            
            # Simple overlay covering the board area
            overlay_rect = pygame.Rect(0, 50, config.WINDOW_WIDTH, config.WINDOW_HEIGHT - 50)
            s = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150)) # Black with transparency
            self.screen.blit(s, (0, 50))
            
            large_font = pygame.font.Font(None, 80)
            text = large_font.render(message, True, color)
            text_rect = text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
            self.screen.blit(text, text_rect)

class InputController:
    """Handles mouse input and converts coordinates to cell indices."""
    def __init__(self, game):
        self.game = game

    def pos_to_grid(self, x, y):
        """Converts screen position to (col, row) and returns (-1, -1) if out of bounds."""
        # Adjust for header offset
        y -= 50
        if y < 0:
            return -1, -1
            
        col = x // config.CELL_SIZE
        row = y // config.CELL_SIZE
        
        if self.game.board.is_inbounds(col, row):
            return col, row
        else:
            return -1, -1

    def handlemouse(self, pos, button):
        # To Do (6점): Process mouse button input (L/R/M click).
        if self.game.board.game_over:
            return
            
        col, row = self.pos_to_grid(pos[0], pos[1])
        if col == -1: # Out of bounds
            return

        if button == config.MOUSE_LEFT:
            # Left Click: Reveal cell
            self.game.board.reveal(col, row)
            
        elif button == config.MOUSE_RIGHT:
            # Right Click: Toggle flag
            self.game.board.toggleflag(col, row)
            
        elif button == config.MOUSE_MIDDLE:
            # Middle Click: Quick reveal/Chord
            
            # Check if the middle-clicked cell is revealed
            cell = self.game.board.cells[self.game.board.index(col, row)]
            if not cell.is_revealed:
                # Highlight logic (optional part of implementation, mainly for visual feedback)
                self.game.highlight_cells = self.game.board.neighbors(col, row)
                return

            # Quick Reveal Logic (Chord)
            # Count surrounding flags
            flag_count = 0
            unrevealed_neighbors = []
            
            for n_col, n_row in self.game.board.neighbors(col, row):
                n_cell = self.game.board.cells[self.game.board.index(n_col, n_row)]
                if n_cell.is_flagged:
                    flag_count += 1
                if not n_cell.is_revealed and not n_cell.is_flagged:
                    unrevealed_neighbors.append((n_col, n_row))

            # If flag count matches adjacent mine count, reveal all unrevealed, unflagged neighbors
            if flag_count == cell.adjacent_mines and cell.adjacent_mines > 0:
                for n_col, n_row in unrevealed_neighbors:
                    self.game.board.reveal(n_col, n_row)


class Game:
    """Manages the main Pygame loop and overall game state."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.CAPTION)
        self.font = pygame.font.Font(None, config.FONT_SIZE)
        
        self.board = Board(config.BOARD_COLS, config.BOARD_ROWS, config.NUM_MINES)
        self.renderer = Renderer(self.screen, self.font)
        self.input_controller = InputController(self)
        
        self.running = True
        self.start_time = None
        self.elapsed_time = 0
        self.clock = pygame.time.Clock()
        self.highlight_cells = [] # Stores (col, row) for cells to highlight

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(30)
            
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if not self.board.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.input_controller.handlemouse(pos, event.button)
                    self.highlight_cells = [] # Clear highlights after click

    def update(self):
        if not self.board._mines_placed:
            # Game hasn't started yet (no valid first click)
            self.start_time = None
            self.elapsed_time = 0
        elif not self.board.game_over:
            if self.start_time is None:
                self.start_time = time.time()
            self.elapsed_time = time.time() - self.start_time
        # If game_over, time freezes at the end time

    def render(self):
        self.screen.fill(config.COLOR_WHITE)
        
        # Draw all cells
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                index = self.board.index(col, row)
                cell = self.board.cells[index]
                self.renderer.draw_cell(col, row, cell)

        # Draw highlights (for middle click preview)
        for col, row in self.highlight_cells:
            self.renderer.draw_highlight(col, row)
            
        # Draw header (Time and Mine count)
        self.renderer.draw_header(self.board, self.elapsed_time)

        # Draw game state message (if game is over)
        self.renderer.draw_game_state_message(self.board)
        
        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()