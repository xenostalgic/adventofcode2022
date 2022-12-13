import sys

import IPython as ipy

def read_input(filename):
    rows = []
    for line in open(filename, "r"):
        row = [ord(ch) if ch not in ["S", "E"] else ch for ch in line.strip()]
        rows.append(row)
    return rows

def index(map, point):
    return map[point[0]][point[1]]

def valid(map, p1, p2):
    if p2[0] >= len(map) or p2[1] >= len(map[0]) or p2[0] < 0 or p2[1] < 0:
        # off the map
        return False
    if (map[p1[0]][p1[1]] == "S") or (map[p2[0]][p2[1]] == "S"):
        # can always transit start
        return True
    if (map[p2[0]][p2[1]] == "E") and (map[p1[0]][p1[1]] >= ord("y")):
        # can transit end from y or z
        return True
    elif (map[p2[0]][p2[1]] == "E"):
        return False
    if (map[p2[0]][p2[1]] - map[p1[0]][p1[1]] < 2):
        # not too steep
        return True
    return False

def a_star(map, start, goal):
    min_paths = {start:([start],0)}
    frontier = [start]
    while len(frontier) > 0:
        p1 = frontier.pop()
        for p2 in [
            (p1[0]+1,p1[1]),
            (p1[0]-1,p1[1]),
            (p1[0],p1[1]+1),
            (p1[0],p1[1]-1),
        ]:
            if p2 == start:
                continue
            try:
                if not valid(map, p1, p2):
                    continue
            except:
                ipy.embed()
            new_path = (min_paths[p1][0]+[p2], min_paths[p1][1]+1)
            if p2 not in min_paths or new_path[1] < min_paths[p2][1]:
                min_paths[p2] = new_path
                frontier.append(p2)
        if goal in min_paths:
            break
        frontier = sorted(frontier, key=lambda p: min_paths[p][1], reverse=True)
    return min_paths[goal]


def q1(filename):
    map = read_input(filename)
    start, goal = None, None
    for i, row in enumerate(map):
        if "S" in row:
            start = (i, row.index("S"))
        if "E" in row:
            goal = (i, row.index("E"))
    best_path = a_star(map, start, goal)
    print("Q1:", best_path[1])


def q2(filename):
    map = read_input(filename)
    goal = None
    for i, row in enumerate(map):
        if "E" in row:
            goal = (i, row.index("E"))
    min_best = 1000
    for i in range(len(map)):
        start = (i,0)
        best_path = a_star(map, start, goal)
        min_best = min(min_best, best_path[1])
    print("Q2:", min_best)


def print_path(map, path):
    map = map.copy()
    for i,p1 in enumerate(path):
        if map[p1[0]][p1[1]] in ["S","E"]:
            continue
        p2 = path[i+1]
        if p1[0]==p2[0]:
            if p1[1] < p2[1]:
                ch = ">"
            elif p1[1] > p2[1]:
                ch = "<"
        elif p1[0] < p2[0]:
            ch = "v"
        else:
            ch = "^"
        map[p1[0]][p1[1]] = ch
    for row in map:
        print("".join(['.' if entry not in list("<>^vSE") else entry for entry in row]))

def print_map(map):
    for row in map:
        line = "".join([chr(entry) if entry not in list("SE") else entry for entry in row])
        print(line)

if __name__=="__main__":
    q1(sys.argv[1])
    q2(sys.argv[1])

        

        

