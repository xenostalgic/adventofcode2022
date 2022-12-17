import sys
import numpy as np
from collections import defaultdict
from functools import cmp_to_key
from tqdm import tqdm

import IPython as ipy

def read_lines(filename, floor=False):
    with open(filename, "r") as f:
        lines = [l.strip() for l in f.readlines()]
    items = {}
    for line in lines:
        ls = line.split()
        sx = int(ls[2][2:-1])
        sy = int(ls[3][2:-1])
        bx = int(ls[-2][2:-1])
        by = int(ls[-1][2:])
        items[(sy,sx)] = (by,bx)
    return items

def print_grid(grid):
    n_leading = 3
    max_row = grid.shape[0]
    max_col = grid.shape[1]
    for row in range(-1,max_row):
        for col in range(max_col):
            val = "."
            if row==-1: 
                if col+2 % 5 == 0: val="*"
            elif grid[row,col] == 0: val="."
            elif grid[row,col] == 1: val = "S"
            elif grid[row,col] == 2: val = "B"
            elif grid[row,col] == 3: val = "#"
            print(val, end="")
        print(".")
    print("")

def manhattan(p1, p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

def no_beacons_row(sensors, row):
    # scan a row for beacon-free positions
    nonb = set()
    bset = set()
    ranges = []
    for spos in sensors:
        bpos = sensors[spos]
        if bpos[0] == row:
            bset.add(bpos[1])
        dist = manhattan(spos, bpos)
        ydist = abs(spos[0]-row)
        if ydist > dist:
            continue
        xdist = dist-ydist
        ranges.append((spos[1]-xdist, spos[1]+xdist+1))
        for j in range(spos[1]-xdist,spos[1]+xdist+1):
            nonb.add(j)
    return len([c for c in nonb if c not in bset])

def no_beacons_grid(sensors, maxv):
    # brute force solution. terrible, do not use
    dists = {spos: manhattan(spos, sensors[spos]) for spos in sensors}
    row = np.zeros(maxv, dtype=bool)
    for row in range(maxv):
        row[:] = 0
        for spos, dist in dists.items():
            rdist = abs(spos[0]-row)
            if rdist > dist:
                continue
            cdist = dist-rdist
            row[spos[1]-cdist:spos[1]+cdist+1] = 1
        mincol = row.argmin()
        if row[mincol] == 0:
            return (row,mincol)
    return None

def trace_edges(sensors, maxv):
    # search only over positions that are one step further from a sensor
    # than its beacon. faster, but still not optimal
    dists = {spos:manhattan(spos, sensors[spos]) for spos in sensors}
    for spos, dist in dists.items():
        for row in range(
            max(spos[0]-dist-1,0),
            min(spos[0]+dist+2,maxv)
        ):
            rdist = abs(spos[0]-row)
            c_offset = dist-rdist+1
            col = spos[1]
            if rdist == dist+1:
                edges = [(row, col)]
            elif rdist <= dist:
                edges = [(row,col-c_offset),(row,col+c_offset)]
            for edge_pos in edges:
                if not ((0 <= edge_pos[0] < maxv) and (0 <= edge_pos[1] < maxv)):
                    continue
                uncovered = True
                for tgt_spos,tgt_dist in dists.items():
                    if tgt_spos == spos:
                        continue
                    if manhattan(tgt_spos,edge_pos) <= tgt_dist:
                        uncovered = False
                        break
                if uncovered:
                    return edge_pos
    return None


def shape_based(sensors, maxv):
    # represent sensor-covered regions as convex hulls, and iteratively merge them
    dists = {spos:manhattan(spos, sensors[spos]) for spos in sensors}
    hulls = []
    for spos1, dist1 in dists.items():
        for spos2, dist2 in dists.items():
            if spos1 == spos2:
                continue
            pdist = manhattan(spos1, spos2)
            if pdist <= (dist1+dist2):
                # these sensor zones overlap; find the convex corners
                pass
            elif pdist == (dist1+dist2+1):
                #then............................. uh
                pass


def q1(filename):
    sensors = read_lines(filename)
    if len(sensors) < 15:
        nb10 = no_beacons_row(sensors, 10)
        print(f"N positions with no beacon in row 10: {nb10}")
    else:
        nb2M = no_beacons_row(sensors, 2000000)
        print(f"N positions with no beacon in row 2000000: {nb2M}") # 4,558,179 < X < 8,068,433

def q2(filename):
    sensors = read_lines(filename)
    if len(sensors) < 15:
        maxv = 20
    else:
        maxv = 4000000
    res = trace_edges(sensors,maxv)
    print("Distress beacon location:", res)
    print(f"Tuning freq: {(res[1]*4000000) + res[0]}")

if __name__=="__main__":
    print("\n== Part 1 ==")
    q1(sys.argv[1])
    print("\n== Part 2 ==")
    q2(sys.argv[1])


