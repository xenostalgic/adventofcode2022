import sys
import numpy as np

import IPython as ipy

def print_grid(grid):
    n_leading = 3
    max_col = grid.shape[0]
    max_row = grid.shape[1]
    min_col = min(grid[:,:-3].nonzero()[0])-5
    for row in range(max_row):
        print(f"{row: >{n_leading}} " ,end="")
        for col in range(min_col, max_col):
            val = "."
            if row==0: 
                if col==500: val="+"
                elif col % 10 == 0: val="*"
            elif grid[col,row] == 0: val="."
            elif grid[col,row] == 1: val = "#"
            elif grid[col,row] == 2: val = "o"
            elif grid[col,row] == 3: val = "~"
            print(val, end="")
        print(".")
    print("")


def read_input(filename, floor=False):
    paths = []
    max_col = 500
    max_row = 0
    for line in open(filename, "r"):
        points = [p.split(",") for p in line.split(" -> ")]
        points = [tuple([int(idx) for idx in p]) for p in points]
        for p in points:
            max_col = max(max_col, p[0])
            max_row = max(max_row, p[1])
        paths.append(points)
    grid = np.zeros((max_col+max_row,max_row+4))
    for path in paths:
        for i in range(len(path)-1):
            p1, p2 = path[i], path[i+1]
            x1 = min(p1[0],p2[0])
            x2 = max(p1[0],p2[0])+1
            y1 = min(p1[1],p2[1])
            y2 = max(p1[1],p2[1])+1
            grid[x1:x2,y1:y2] = 1
    if floor:
        grid[:,max_row+2] = 1
    print_grid(grid)
    return grid


def run_sim(grid):
    falling = False
    n_grains = 0
    while not falling: # loop over sand grains
        n_grains += 1
        pos = (500,0)
        path = [pos]
        settled = False
        if grid[pos] == 2:
            print(f"Source of sand is blocked after {n_grains-1} grains of sand")
            break
        while not settled: # update position of this grain
            d = (pos[0],pos[1]+1)
            l = (pos[0]-1,pos[1]+1)
            r = (pos[0]+1,pos[1]+1)
            if pos[1] >= grid.shape[1]-1:
                falling = True
                for p in path:
                    grid[p] = "3"
                print(f"grain {n_grains} is falling at col {pos[0]}")
                break
            elif grid[d] == 0:
                pos = d
            elif grid[l] == 0:
                pos = l
            elif grid[r] == 0:
                pos = r
            else:
                settled = True
            path.append(pos)
        if not falling:
            grid[pos] = 2
            print(f"settled grain {n_grains} at position {pos}")
        # print_grid(grid)
        # if n_grains > 0:
        #     break
    print(f"Final state (n={n_grains-1}):")
    print_grid(grid)

def q1(filename):
    grid = read_input(filename)
    run_sim(grid)

def q2(filename):
    grid = read_input(filename, floor=True)
    run_sim(grid)

if __name__=="__main__":
    print("\n== Part 1 ==")
    # q1(sys.argv[1])
    print("\n== Part 2 ==")
    q2(sys.argv[1])


