import random

COLS = 0
ROWS = 0
BOARD = []
WINNIG = []

def setup_board(cols: int, rows: int):
    global COLS, ROWS, BOARD
    COLS = cols
    ROWS = rows
    BOARD = [[0 for _ in range(COLS)] for _ in range(ROWS)]

def is_valid_move(col):
    global BOARD
    return BOARD[0][col] == 0

def easy_computer_move():
    global COLS
    available_cols = [c for c in range(COLS) if is_valid_move(c)]
    return random.choice(available_cols) if available_cols else -1

def medium_computer_move(player):
    global COLS, WINNIG
    available_cols = []

    for i in WINNIG:
        pl, on, r, c = i

        if pl != player:
            available_cols.append(c)

            if on == 3:
                if r == 0:
                    return c
                elif BOARD[r-1][c] != 0:
                    return c

    
    WINNIG.clear()

    if len(available_cols) == 0:
        return easy_computer_move()
    
    return random.choice(available_cols) if available_cols else -1
    
def hard_computer_move(player):
    global COLS, WINNIG
    available_cols = []
    weights = []

    for i in WINNIG:
        pl, on, r, c = i

        if pl != player:
            available_cols.append(c)
            weights.append(on + 33)
            
            if on == 3:
                if r == 0:
                    return c
                elif BOARD[r-1][c] != 0:
                    return c
            
        else:
            if on == 3:
                available_cols.append(c)
                weights.append(on + 100)
            else:
                available_cols.append(c)
                weights.append(on + 50)
    
    # for i in weights:


    # WINNIG.clear()

    if len(available_cols) == 0:
        return easy_computer_move()

    return random.choice(available_cols) if available_cols else -1

def make_move(col, player):
    global ROWS, BOARD
    if not is_valid_move(col):
        return False
    for row in range(ROWS-1, -1, -1):
        if BOARD[row][col] == 0:
            BOARD[row][col] = player
            return True
    return False

def check_winner():
    global BOARD, ROWS, COLS, WINNIG
    WINNIG.clear()
    for row in range(ROWS):
        for col in range(COLS):
            if BOARD[row][col] != 0 and (
                check_line(row, col, 1, 0) or  # vertical
                check_line(row, col, 0, 1) or  # horizontal
                check_line(row, col, 1, 1) or  # diagonal /
                check_line(row, col, 1, -1)   # diagonal \
            ):
                return BOARD[row][col]
    return 0

def check_line(row, col, delta_row, delta_col):
    global BOARD, ROWS, COLS, WINNIG
    start = BOARD[row][col]
    for i in range(1, 4):
        r, c = row + i * delta_row, col + i * delta_col
        if r < 0 or r >= ROWS or c < 0 or c >= COLS or BOARD[r][c] != start:
            if i >= 2 and r >= 0 and c >= 0 and r < ROWS and c < COLS and BOARD[r][c] == 0:
                save = (start, i-1, r,c)
                WINNIG.append(save)
            return False
        # have a tuple of list (player, 
    return True