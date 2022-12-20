import sys
import numpy as np
import itertools
from tqdm import tqdm

import IPython as ipy

ADJ = [
    (0,0,1),
    (0,0,-1),
    (0,1,0),
    (0,-1,0),
    (1,0,0),
    (-1,0,0),
]

P = [-1,0,1]
NEAR = [c for c in list(itertools.product(P,P,P)) if c != (0,0,0)]

def read_input(filename):
    coords = []
    for line in open(filename):
        coords.append(tuple([int(x) for x in line.strip().split(",")]))
    return set(coords)

def plus(c1,c2):
    return (c1[0]+c2[0], c1[1]+c2[1], c1[2]+c2[2])

def dist(c1,c2):
    return abs(c1[0]-c2[0]) + abs(c1[1]-c2[1]) + abs(c1[2]-c2[2])

def neighbors(cube):
    return [plus(cube,adj) for adj in ADJ]

def nearby(cube):
    near = [plus(plus(cube,adj1),adj2) for adj1,adj2 in itertools.combinations(ADJ,3)]
    return [c for c in near if c != cube]

def get_limits(coords):
    x1 = max([c[0] for c in coords])
    y1 = max([c[1] for c in coords])
    z1 = max([c[2] for c in coords])
    x2 = min([c[0] for c in coords])
    y2 = min([c[1] for c in coords])
    z2 = min([c[2] for c in coords])
    return (x1,y1,z1), (x2,y2,z2)

def get_surface_area(coords):
    # O(N*6*log(n))
    surface_area = 0
    print("Max surface area (# cubes x # sides) =", len(coords)*6)
    for c1 in coords:
        for c2 in neighbors(c1):
            if c2 not in coords:
                surface_area += 1
    return surface_area

def min_dist(coords,cube):
    dists = [dist(cube,c) for c in coords]
    return min(dists) 

def get_exterior(coords):
    # O(6N) to get points in surface
    # ~O(6*6N) to loop over neighbors of surface points
    surface = set()
    for c1 in coords:
        for c2 in neighbors(c1):
            if c2 not in coords:
                surface.add(c2)
    exterior = set()
    visited = set()
    queue = [max(surface, key=lambda x: x[0])]
    while queue:
        p = queue.pop()
        visited.add(p)
        nearby = []
        add_n = False
        for n in neighbors(p):
            if n in coords:
                exterior.add(p)
                add_n = True
        if add_n:
            nearby += neighbors(p)
            for n in neighbors(p):
                if n not in coords:
                    nearby += neighbors(n)
        nearby = [n for n in nearby if n not in visited and n not in coords]
        queue += nearby

    exterior_surface = 0
    for c1 in exterior:
        for c2 in neighbors(c1):
            if c2 in coords:
                exterior_surface += 1
    return exterior_surface


if __name__=="__main__":
    coords = read_input(sys.argv[1])
    print("== Part 1 ==")
    surface_area = get_surface_area(coords)
    print("Surface area:", surface_area)
    print("== Part 2 ==")
    exterior_surface = get_exterior(coords)
    print("Exterior surface area:", exterior_surface)
