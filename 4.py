import sys

import IPython as ipy


def fully_contained(r1, r2):
    r1 = [int(x) for x in r1.split("-")]
    r2 = [int(x) for x in r2.split("-")]

    if r1[0] >= r2[0] and r1[1] <= r2[1]:
        # r2 fully contains r1
        return True
    if r2[0] >= r1[0] and r2[1] <= r1[1]:
        # r1 fully contains r2
        return True
    return False

def any_overlap(r1, r2):
    r1 = [int(x) for x in r1.split("-")]
    r2 = [int(x) for x in r2.split("-")]

    if r1[0] >= r2[0] and r1[0] <= r2[1]:
        return True
    if r1[0] <= r2[0] and r1[1] >= r2[0]:
        return True
    return False


def parse_file(filename):
    n_fully_contains = 0
    n_overlap = 0
    for line in open(filename, "r"):
        r1, r2 = line.strip().split(",")
        if fully_contained(r1,r2):
            print(line)
            n_fully_contains += 1
        if any_overlap(r1, r2):
            n_overlap += 1
    return n_fully_contains, n_overlap

if __name__=="__main__":
    n_fully_contains, n_overlap = parse_file(sys.argv[1])
    print(f"{n_fully_contains} pairs where one fully contains the other")
    print(f"{n_overlap} pairs with overlap")
