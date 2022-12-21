import sys
import numpy as np
from tqdm import tqdm

import IPython as ipy

def read_input(filename):
    input = []
    for line in open(filename, "r"):
        input.append(int(line.strip()))
    return input

def get_canonical_order(nums, loc_map):
    state = []
    for i in range(len(nums)):
        idx = np.where(loc_map==i)[0].item()
        state.append(nums[idx])
    return state

def print_state(nums, loc_map):
    state = get_canonical_order(nums, loc_map)
    print("", state[:10])

def mix(nums, rounds=1):
    n = len(nums)
    # idx indexes original order
    # loc indexes current order
    # maps idx -> loc
    loc_map = np.zeros((n,), dtype=np.int32)
    for i in range(n):
        loc_map[i] = i
    debug = (n < 1000)
    if debug:
        print("initial state:")
        print_state(nums, loc_map)

    for r in range(rounds):
        for idx in range(n):
            loc = loc_map[idx]
            upd_val = nums[idx] 
            # if it wraps all the way around, no change. also converts negatives
            new_loc = (loc + upd_val) % (n-1)
            if new_loc == loc%(n-1): # i.e. both in (0,n-1)
                continue
            if loc < new_loc:
                upd_idxs = np.nonzero((loc_map > loc) & (loc_map <= new_loc))
                loc_map[upd_idxs] = (loc_map[upd_idxs] - 1) % n
                # for upd_idx in range(n):
                #     if loc < loc_map[upd_idx] <= new_loc:
                #         loc_map[upd_idx] = (loc_map[upd_idx] - 1) % n
                loc_map[idx] = new_loc
            elif new_loc < loc:
                upd_idxs = np.nonzero((loc_map < loc) & (loc_map >= new_loc))
                loc_map[upd_idxs] = (loc_map[upd_idxs] + 1) % n
                # for upd_idx in range(n):
                #     if new_loc <= loc_map[upd_idx] < loc:
                #         loc_map[upd_idx] = (loc_map[upd_idx] + 1) % n
                loc_map[idx] = new_loc
        if debug:
            print(f"After {r+1} rounds of mixing:")
            print_state(nums, loc_map)
    output = get_canonical_order(nums, loc_map)
    zero = output.index(0)
    coords = []
    for c in [1000,2000,3000]:
        coords.append(output[(zero+c)%n])
    print("Sum:", sum(coords))

            
if __name__=="__main__":
    nums = read_input(sys.argv[1])
    print("== Part 1 ==")
    mix(nums, rounds=1)
    print("== Part 2 ==")
    nums = [v*811589153 for v in nums]
    mix(nums, rounds=10)

