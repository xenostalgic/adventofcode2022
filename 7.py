import sys

import IPython as ipy

def get_dir_structure(lines):
    children = {}
    parents = {}
    files = {}
    i = 0
    cur_dir = "/"
    while i < len(lines):
        print(lines[i].strip())
        if cur_dir not in children:
            children[cur_dir] = []
        if cur_dir not in files:
            files[cur_dir] = []
        if lines[i].startswith("$ ls"):
            j = 1
            output = []
            while ((i+j) < len(lines)) and (lines[i+j][0] != "$"):
                output.append(lines[i+j])
                j += 1
            print("".join(output))
            for entry in output:
                entry = entry.split()
                if entry[0] == "dir":
                    subdir = f"{cur_dir}/{entry[1]}"
                    children[cur_dir].append(subdir)
                    parents[subdir] = cur_dir
                else:
                    files[cur_dir].append(int(entry[0]))
            i = i+j
        elif lines[i].startswith("$ cd"):
            tgt = lines[i].strip().split()[-1]
            if tgt == "..":
                cur_dir = parents[cur_dir]
            elif tgt == "/":
                cur_dir = "/"
            else:
                dest = f"{cur_dir}/{tgt}"
                if dest not in children[cur_dir]:
                    print(f"warning: adding {dest} as a child of {cur_dir} in line {i}")
                    children[cur_dir].append(dest)
                    if dest == cur_dir:
                        print("adding self as child")
                        ipy.embed()
                parents[dest] = cur_dir
                cur_dir = dest
            i += 1
    for d in parents:
        assert d in children[parents[d]]
    return parents, children, files

def get_total(children, files, d):
    print(d)
    if d in children:
        return sum(files[d]) + sum([get_total(children, files, cd) for cd in children[d]])
    else:
        return sum(files[d])

def q1(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        parents, children, files = get_dir_structure(lines)
    totals = {d:0 for d in files}
    for d in set(list(children.keys()) + list(files.keys()) + list(parents.keys())):
        totals[d] = get_total(children, files, d)
    match_sum = sum([t for t in totals.values() if t < 100000])
    print(totals)
    print(f"Sum of dir totals < 100k: {match_sum}")

def q2(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        parents, children, files = get_dir_structure(lines)
    totals = {d:0 for d in files}
    for d in set(list(children.keys()) + list(files.keys()) + list(parents.keys())):
        totals[d] = get_total(children, files, d)
    free_space = 70000000 - totals["/"]
    print(f"{free_space} free")
    needed_space = 30000000 - free_space
    print(f"{needed_space} needed for update")
    for dir in sorted(totals, key=totals.get):
        if totals[dir] > needed_space:
            print(totals[dir], dir)
            break
        else:
            print(totals[dir])

if __name__=="__main__":
    q1(sys.argv[1])
    q2(sys.argv[1])
                        

            

