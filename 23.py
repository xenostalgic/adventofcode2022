from collections import Counter
from typing import Optional
import numpy as np
import sys
from tqdm import tqdm

import IPython as ipy

def get_directions(step_idx: int):
    DIRS = [
        {"name": "north", "target": (-1,0), "check": [(-1,-1), (-1,0), (-1,1)]},
        {"name": "south", "target": (1,0), "check": [(1,-1), (1,0), (1,1)]},
        {"name": "west", "target": (0,-1), "check": [(-1,-1), (0,-1), (1,-1)]},
        {"name": "east", "target": (0,1), "check": [(-1,1), (0,1), (1,1)]},
    ]
    mod_idx = (step_idx % 4)
    return DIRS[mod_idx:] + DIRS[:mod_idx]

def read_set(lines):
    positions = []
    for i, line in enumerate(lines):
        for j, ch in enumerate(line):
            if ch == "#":
                positions.append((i,j))
    return set(positions)


def set_neighbors(dir_name: Optional[str]=None) -> list[tuple]:
    neighbors = []
    if dir_name is None:
        i_s = [-1,0,1]
        j_s = [-1,0,1]
    if dir_name == "north":
        i_s = [-1]
        j_s = [-1,0,1]
    elif dir_name == "south":
        i_s = [1]
        j_s = [-1,0,1]
    if dir_name == "west":
        j_s = [-1]
        i_s = [-1,0,1]
    elif dir_name == "east":
        j_s = [1]
        i_s = [-1,0,1]
    for i in i_s:
        for j in j_s:
            neighbors.append((i,j))
    return neighbors



def step_set_sim(positions: set, step_idx: int = 0):
    dirs = get_directions(step_idx)
    proposed_positions = []

    # get proposed positions
    for pos in positions:
        ei,ej = pos
        pos_neighbors = set([(ei+ni,ej+nj) for (ni,nj) in set_neighbors()])
        prop = (ei,ej)
        if len(pos_neighbors.intersection(positions)) > 1:
            for dir in dirs:
                dir_neighbors = set([(ei+ni,ej+nj) for (ni,nj) in set_neighbors(dir_name=dir["name"])])
                if len(dir_neighbors.intersection(positions)) == 0:
                    ti,tj = dir["target"]
                    prop = (ei+ti,ej+tj)
                    break
        proposed_positions.append(prop)
    
    # execute and check for conflicts
    new_positions = []
    prop_counts = Counter(proposed_positions)
    for orig, prop in zip(positions, proposed_positions):
        if prop_counts[prop] > 1:
            # conflict; can't move
            new_positions.append(orig)
        else:
            new_positions.append(prop)

    if len(set(new_positions)) != len(positions):
        ipy.embed()

    return set(new_positions)


def covered_ground_set(positions: set) -> int:
    ys, xs = zip(*list(positions))
    miny, maxy = min(ys), max(ys)
    minx, maxx = min(xs), max(xs)
    tot = (maxy+1-miny)*(maxx+1-minx)
    return tot - len(positions)


##############################################


def read_array(lines):
    h = len(lines)
    w = len(lines[0])
    arr = np.zeros((h,w))
    for i, line in enumerate(lines):
        arr[i,:] = np.array([1 if ch == "#" else 0 for ch in line])
    return arr


def print_array(arr):
    h,w = arr.shape
    for i in range(h):
        print("".join(["#" if v else "." for v in arr[i,:]]))


def pad_array(arr: np.ndarray, y: int = 0, x: int = 0):
    h, w = arr.shape
    nh, nw = h+(2*y), w+(2*x)
    new_arr = np.zeros((nh, nw))
    new_arr[y:h+y, x:w+x] = arr
    return new_arr


def trim_array(arr: np.ndarray):
    ys, xs = np.where(arr)
    miny, maxy = min(ys), max(ys)
    minx, maxx = min(xs), max(xs)
    new_arr = arr[miny:maxy+1, minx:maxx+1].copy()
    return new_arr


def step_arr_sim(arr: np.ndarray, step_idx: int = 0) -> np.ndarray:
    """Update the array one step according to the procedure in Part 1.

    Args:
        arr (np.ndarray): An array representing elf positions.
        step_idx (int, optional): The index of the step, used to determine the order of
            directions for proposed movement. Defaults to 0.

    Returns:
        np.ndarry: The updated array.
    """
    h,w = arr.shape
    ys, xs = np.where(arr > 0)
    elves = list(zip(list(ys), list(xs)))
    miny, maxy = min(ys), max(ys)
    minx, maxx = min(xs), max(xs)

    # pad array if needed
    if (miny == 0) or (minx == 0) or (maxy == arr.shape[0]-1) or (maxx == arr.shape[1]-1):
        pad_size = 6
        arr = pad_array(arr, pad_size, pad_size)
        elves = [(ei+pad_size, ej+pad_size) for (ei, ej) in elves]
        h,w = arr.shape

    dirs = get_directions(step_idx)

    # get proposed moves
    prop_moves = []
    for (ei, ej) in elves:
        region = arr[ei-1:ei+2,ej-1:ej+2]
        proposal = None
        if region.sum() == 1:
            # elf is alone
            prop_moves.append(proposal)
            continue
        for dir in dirs:
            ti,tj = dir["target"]
            pi, pj = ei+ti, ej+tj
            if not (0 <= pi < h) and (0 <= pj < w):
                # out of bounds - must be clear
                print(f"moving elf at {(ei,ej)} {dir['name']} out of bounds to {(pi,pj)}")
                proposal = (pi, pj)
                break
            if not any(arr[ci+ei, cj+ej] for (ci,cj) in dir["check"]):
                # direction is clear
                # print(f"moving elf at {(ei,ej)} {dir['name']} to {(pi,pj)}")
                proposal = (pi, pj)
                break
        prop_moves.append(proposal)

    # execute proposed moves
    new_positions = []
    prop_counts = Counter(prop_moves)
    for elf, prop in zip(elves, prop_moves):
        if prop_counts[prop] > 1:
            # conflict; no move
            new_positions.append(elf)
            continue
        new_positions.append(prop)

    # create new array - no expansion needed
    new_arr = np.zeros_like(arr)
    for pos in new_positions:
        new_arr[pos] = 1

    return new_arr, new_positions


def covered_ground_arr(arr: np.ndarray) -> int:
    ys, xs = np.where(arr > 0)
    elves = list(zip(list(ys), list(xs)))
    miny, maxy = min(ys), max(ys)
    minx, maxx = min(xs), max(xs)
    tot = (maxy+1-miny)*(maxx+1-minx)
    return tot - len(elves)


def compare_pos_sets(pos1: set, pos2: set):
    miny1 = min([py for py,px in pos1])
    minx1 = min([px for py,px in pos1])
    miny2 = min([py for py,px in pos2])
    minx2 = min([px for py,px in pos2])
    pos1_base = set([(py-miny1, px-minx1) for py,px in pos1])
    pos2_base = set([(py-miny2, px-minx2) for py,px in pos2])
    return pos1_base == pos2_base



if __name__=="__main__":
    input = [line.strip() for line in open(sys.argv[1])]

    initial_arr = read_array(input)
    step_arr = initial_arr.copy()
    arr_steps = [step_arr]

    initial_pos = read_set(input)
    step_pos = initial_pos.copy()
    pos_steps = [step_pos]

    for step_idx in tqdm(range(1000)):
        step_pos = step_set_sim(step_pos, step_idx)
        step_arr, arr_pos = step_arr_sim(step_arr, step_idx)
        if len(step_pos) != len(initial_pos):
            print("Length changed")
            ipy.embed()
        if not compare_pos_sets(step_pos, arr_pos):
            print("Positions don't match:")
            ipy.embed()
        cgs = covered_ground_set(step_pos)
        cga = covered_ground_arr(step_arr)

        if step_pos == pos_steps[-1]:
            print("Part 2: number of steps to convergence")
            print(step_idx)
            break

        pos_steps.append(step_pos)
        arr_steps.append(step_arr)

        if step_idx == 10:
            print("Part 1: ground covered at step 10")
            print(cgs)

        


        
        
        

    
