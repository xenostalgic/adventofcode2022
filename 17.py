import sys
import numpy as np
from tqdm import tqdm

import IPython as ipy

ROCKS = [
    "flat",
    "cross",
    "l",
    "tall",
    "square"
]
WIDTHS = [4,3,3,1,2]
HEIGHTS = [1,3,3,4,2]
GRIDS = []

def define_grids():
    for i,name in enumerate(ROCKS):
        grid = np.zeros((HEIGHTS[i],WIDTHS[i]),dtype=np.bool)
        if name == "flat":
            grid[0,0:4] = 1
        elif name == "cross":
            grid[1,0:3] = 1
            grid[0:3,1] = 1
        elif name == "l":
            grid[0,0:3] = 1
            grid[0:3,2] = 1
        elif name == "tall":
            grid[0:4,0] = 1
        elif name == "square":
            grid[0:2,0:2] = 1
        GRIDS.append(grid)

def read_input(filename):
    with open(filename) as f:
        pattern = f.read().strip()
        pattern = ["L" if ch=="<" else "R" for ch in pattern]
    return pattern

def intersects(rock_idx, row, col, board):
    w,h = WIDTHS[rock_idx], HEIGHTS[rock_idx]
    grid = GRIDS[rock_idx]
    return board[row:row+h,col:col+w][grid].any()

def print_board(board):
    max_row = np.argmax(board,axis=0).max() + 4
    chmap = [".", "#", "%", "X"]
    for i in range(max_row,0,-1):
        ch_row = "".join(chmap[board[i,j]] for j in range(7))
        print(f"|{ch_row}|")
    print("+-------+")

def print_state(board, row, col, rock_idx):
    new_board = board.copy()
    new_board[row:row+HEIGHTS[rock_idx],col:col+WIDTHS[rock_idx]] += (GRIDS[rock_idx]*2)
    print_board(new_board)

def max_row(board):
    nonzero_rows = np.nonzero(board)[0]
    if len(nonzero_rows) == 0:
        return 0
    return nonzero_rows[-1]

def run_sim(pattern, n_rocks):
    board_height = min(3000,n_rocks*4)
    board = np.zeros((n_rocks*4,7), dtype=np.int8) # max height
    tick = 0
    for i in tqdm(range(n_rocks)):
        rock_idx = i % len(ROCKS)
        rock_w = WIDTHS[rock_idx]
        rock_h = HEIGHTS[rock_idx]
        row = max_row(board) + 4
        if row > board.shape[0] - 10:
            # extend board
            new_board = np.zeros((board_height*2,7))
            new_board[:board_height, :] = board
            board = new_board
            board_height = board.shape[0]
        col = 2
        rtick = 0
        settled = False
        while not settled:
            jet = pattern[tick % len(pattern)]
            if jet == "L":
                if col > 0 and (rtick < 3 or not intersects(rock_idx,row,col-1,board)):
                    col -= 1
            if jet == "R":
                if col < 7-rock_w and (rtick < 3 or not intersects(rock_idx,row,col+1,board)):
                    col += 1
            if rtick >= 2 and (row == 1 or intersects(rock_idx,row-1,col,board)):
                board[row:row+rock_h,col:col+rock_w] += GRIDS[rock_idx]
                settled = True
            else:
                row = row - 1
            tick += 1
            rtick += 1
    print("Max height:", max_row(board))

if __name__=="__main__":
    define_grids()
    if len([ch for ch in sys.argv[1] if ch in "<>"]) == len(sys.argv[1]):
        pattern = ["L" if ch=="<" else "R" for ch in sys.argv[1]]
    else:
        pattern = read_input(sys.argv[1])
    print("== Part 1 ==")
    run_sim(pattern,2022)
    # print("== Part 2 ==")
    # run_sim(pattern,1000000000000)