import sys

import IPython as ipy

def get_priority(char):
    if ord(char) < 91: # A-Z have priorities 27-52
        p = ord(char)-38
    else: #a-z have priorities 1-26
        p = ord(char)-96
    return p

def count_errors(filename):
    tot_p = 0
    for line in open(filename, "r"):
        items = line.strip()
        n = int(len(items)/2)
        c1, c2 = items[:n], items[n:]
        assert(len(c1) == len(c2))
        overlap = list(set(c1).intersection(c2))
        assert(len(overlap)==1)
        char = overlap[0]
        p = get_priority(char)
        tot_p += p
        print(f"Found item {char} with priority {p}")
    return tot_p

def find_group_matches(filename):
    tot_p = 0
    group = []
    for i,line in enumerate(open(filename, "r")):
        group.append(line.strip())
        if (i+1)%3 == 0:
            base = set(group[0])
            for g in group[1:]:
                base = base.intersection(g)
            if len(base) != 1:
                ipy.embed()
            badge = list(base)[0]
            print("Group", group, "has badge", badge)
            p = get_priority(badge)
            tot_p += p
            group = []
    return tot_p


if __name__=="__main__":
    # tot_errors = count_errors(sys.argv[1])
    # print("Errors:", tot_errors)
    badge_sum = find_group_matches(sys.argv[1])
    print("Badge sum:", badge_sum)