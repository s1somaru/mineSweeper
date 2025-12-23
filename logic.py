# logic.py
import random
import consts as c

def initialize_board(size, num_mines):
    board = [[0] * size for _ in range(size)]
    display = [[c.UNOPENED] * size for _ in range(size)]
    
    mines_placed = 0
    while mines_placed < num_mines:
        r, c_idx = random.randint(0, size - 1), random.randint(0, size - 1)
        if board[r][c_idx] != c.MINE:
            board[r][c_idx] = c.MINE
            mines_placed += 1
            
    for r in range(size):
        for col in range(size):
            if board[r][col] == c.MINE:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, col + dc
                    if (0 <= nr < size) and (0 <= nc < size) and (board[nr][nc] == c.MINE):
                        count += 1
            board[r][col] = count
    return board, display

def open_cell(board, display, r, col, size):
    if not (0 <= r < size and 0 <= col < size): return
    if display[r][col] != c.UNOPENED: return
    
    if board[r][col] == c.MINE:
        display[r][col] = c.MINE
        return "GAME_OVER"
    
    display[r][col] = board[r][col]
    
    if board[r][col] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                open_cell(board, display, r + dr, col + dc, size)

def toggle_flag(display, r, c_idx):
    if display[r][c_idx] == c.UNOPENED:
        display[r][c_idx] = c.FLAGGED
    elif display[r][c_idx] == c.FLAGGED:
        display[r][c_idx] = c.UNOPENED

def check_win(display, size, num_mines):
    unopened_or_flagged = 0
    for r in range(size):
        for col in range(size):
            if display[r][col] == c.UNOPENED or display[r][col] == c.FLAGGED:
                unopened_or_flagged += 1
    return unopened_or_flagged == num_mines