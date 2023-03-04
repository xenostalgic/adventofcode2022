import sys
import numpy as np
import IPython as ipy

FACE_IDX = ">v<^"

REGIONS = {
    "A": ((0,50),(50,100)),
    "B": ((0,50),(100,150)),
    "C": ((50,100),(50,100)),
    "D": ((100,150),(0,50)),
    "E": ((100,150),(50,100)),
    "F": ((150,200),(0,50)),
}

def read_input(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    h = len(lines)-2
    w = max([len(l.strip("\n")) for l in lines[:-2]])
    map = np.zeros((h,w), dtype=np.int16)
    for row,line in enumerate(lines[:-2]):
        for col,ch in enumerate(line):
            if ch == ".":
                map[row,col] = 1
            elif ch == "#":
                map[row,col] = 2
    desc = lines[-1].strip()
    path = []
    cur_num = ""
    for ch in desc:
        if ch not in "RL":
            cur_num += ch
        else:
            path.append(int(cur_num))
            path.append(ch)
            cur_num = ""
    if len(cur_num) > 0:
        path.append(int(cur_num))
    return map, path

def print_map(map):
    for i in range(map.shape[0]):
        for j in range(map.shape[1]):
            print(" .#>v<^"[map[i,j]], end='')
        print("")       

def next(pos,face):
    if face == 0:
        pos = pos[0],pos[1]+1
    if face == 1:
        pos = pos[0]+1,pos[1]
    if face == 2:
        pos = pos[0],pos[1]-1
    if face == 3:
        pos = pos[0]-1,pos[1]
    return pos

def wrap(pos,face,map):
    if face == 0:
        pos = pos[0], np.nonzero(map[pos[0],:] > 0)[0].min()
    if face == 1:
        pos = np.nonzero(map[:,pos[1]] > 0)[0].min(), pos[1]
    if face == 2:
        pos = pos[0], np.nonzero(map[pos[0],:] > 0)[0].max()
    if face == 3:
        pos = np.nonzero(map[:,pos[1]] > 0)[0].max(), pos[1]
    return pos

"""
practice:
..A
BCD.
..EF

main:
.AB
.C.
DE.
F..
"""

def fold_cube(map):
    if map.shape[0] > 100:
        region_dirs = {
            "A": {">":"B>", "<":"D>", "^":"F>", "v":"Cv"},
            "B": {">":"E<", "<":"A<", "^":"F^", "v":"C<"},
            "C": {">":"B^", "<":"Dv", "^":"A^", "v":"Ev"},
            "D": {">":"E>", "<":"A>", "^":"C>", "v":"Fv"},
            "E": {">":"B<", "<":"D<", "^":"C^", "v":"F<"},
            "F": {">":"E^", "<":"Av", "^":"D^", "v":"Bv"},
        }
    return region_dirs

def wrap_cube(pos,face,regions):
    for rname,ridx_range in REGIONS.items():
        row_range = ridx_range[0]
        col_range = ridx_range[1]
        if pos[0] in range(row_range[0],row_range[1]) and pos[1] in range(col_range[0],col_range[1]):
            break
    dir_map = regions[rname]
    face = FACE_IDX[face]
    tgt = dir_map[face]
    next_region = tgt[0]
    next_face = tgt[1]
    if face in "><":
        offset = pos[0] - ridx_range[0][0]
    elif face in "v^":
        offset = pos[1] - ridx_range[1][0]

    try:
        if next_face == ">":
            next_pos = (offset + REGIONS[next_region][0][0], REGIONS[next_region][1][0])
        elif next_face == "<":
            next_pos = (offset + REGIONS[next_region][0][0], REGIONS[next_region][1][1]-1)
        elif next_face == "v":
            next_pos = (REGIONS[next_region][0][0], offset + REGIONS[next_region][1][0])
        elif next_face == "^":
            next_pos = (REGIONS[next_region][0][1]-1, offset + REGIONS[next_region][1][0])
    except:
        print("\nerror indexing for next pos calculation\n")
        ipy.embed()

    try:
        v = map[next_pos]
    except:
        print("\nnext pos is off map\n")
        ipy.embed()

    print(f"\nWrapped from {rname} to {next_region}")

    return next_pos, FACE_IDX.index(next_face)

def follow_path(map, path):
    pos = (0,np.nonzero(map[0,:] == 1)[0].min())
    face = FACE_IDX.index(">")
    map[pos] = 3+face
    for step_idx, step in enumerate(path):
        if step == "R":
            # turn 90° right from current heading
            face = (face + 1) % 4
            map[pos] = 3+face
            msg = f"Turned 90° right, now facing {FACE_IDX[face]}"
        elif step == "L":
            # turn 90° left from current heading
            face = (face - 1) % 4
            map[pos] = 3+face
            msg = f"Turned 90° left, now facing {FACE_IDX[face]}"
        else:
            # move k steps forward (check for walls and wrapping)
            i = 0
            while i < step:
                next_pos = next(pos, face)
                if next_pos[0] >= map.shape[0] or next_pos[1] >= map.shape[1]:
                    # off the edge of the map; wrap around
                    print(f"Step {step_idx}: need to edge-wrap after {pos} to {next_pos}; ", end='')
                    next_pos = wrap(pos,face,map)
                    print(f"new next pos and facing: {next_pos}, {face}")
                elif map[next_pos] == 0:
                    # off the marked map; wrap around
                    print(f"Step {step_idx}: need to map-wrap after {pos} to {next_pos}; ", end='')
                    next_pos = wrap(pos,face,map)
                    print(f"new next pos and facing: {next_pos}, {face}")
                if map[next_pos] == 2: # wall; done moving
                    break
                pos = next_pos
                map[pos] = face + 3
                i += 1
            msg = f"Moved {i} steps {FACE_IDX[face]} to {pos}"
            if i+1 < step:
                msg += f" (blocked after {i}/{step} by a wall at {next_pos}"
        print(f"Step {step_idx}:", msg)
    r, c, f = pos[0]+1, pos[1]+1, face
    print("Final position and facing:", r, c, f)
    pwd = 1000*r + 4*c + f
    return pwd

def follow_cube_path(map, regions, path):
    pos = (0,np.nonzero(map[0,:] == 1)[0].min())
    face = FACE_IDX.index(">")
    map[pos] = 3+face
    for step_idx, step in enumerate(path):
        if step == "R":
            # turn 90° right from current heading
            face = (face + 1) % 4
            map[pos] = 3+face
            msg = f"Turned 90° right, now facing {FACE_IDX[face]}"
        elif step == "L":
            # turn 90° left from current heading
            face = (face - 1) % 4
            map[pos] = 3+face
            msg = f"Turned 90° left, now facing {FACE_IDX[face]}"
        else:
            # move k steps forward (check for walls and wrapping)
            i = 0
            while i < step:
                next_pos = next(pos, face)
                next_face = face
                if next_pos[0] >= map.shape[0] or next_pos[1] >= map.shape[1]:
                    # off the edge of the map; wrap around
                    print(f"Step {step_idx}: need to edge-wrap after {pos} to {next_pos}; ", end='')
                    next_pos, next_face = wrap_cube(pos,face,regions)
                    print(f"new next pos and facing: {next_pos}, {next_face}")
                elif map[next_pos] == 0:
                    # off the marked map; wrap around
                    print(f"Step {step_idx}: need to map-wrap after {pos} to {next_pos}; ", end='')
                    next_pos, next_face = wrap_cube(pos,face,regions)
                    print(f"new next pos and facing: {next_pos}, {next_face}")
                if map[next_pos] == 2: # wall; done moving
                    break
                pos = next_pos
                face = next_face
                map[pos] = face + 3
                i += 1
            msg = f"Moved {i} steps {FACE_IDX[face]} to {pos}"
            if i+1 < step:
                msg += f"(blocked after {i}/{step} by a wall at {next_pos}"
        print(f"Step {step_idx}:", msg)
    r, c, f = pos[0]+1, pos[1]+1, face
    print("Final position and facing:", r, c, f)
    pwd = 1000*r + 4*c + f
    return pwd

if __name__=="__main__":
    map, path = read_input(sys.argv[1])
    # print("== Part 1 ==")
    # pwd = follow_path(map, path)
    # print("Password:", pwd)
    print("== Part 2 ==")
    regions = fold_cube(map)
    pwd = follow_cube_path(map, regions, path)
    print("Password:", pwd) # > 4408
