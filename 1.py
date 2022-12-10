import sys

import IPython as ipy

def max_group(filename):
    cur_sum, max_sum = 0, 0
    for line in open(filename):
        if len(line.strip()) == 0:
            if cur_sum > max_sum:
                max_sum = cur_sum
            cur_sum = 0
        else:
            cur_sum += int(line.strip())
    return max_sum

def max_queue(filename, n=3):
    top = [0]*n
    cur_sum = 0
    for line in open(filename):
        if len(line.strip()) == 0:
            if cur_sum > min(top):
                top = sorted(top + [cur_sum])[1:]
            cur_sum = 0
        else:
            cur_sum += int(line.strip())
    return top

def gather(filename):
    input = open(filename, "r").read()
    elves = input.split("\n\n")
    elf_cals = [(idx,sum([int(cal) for cal in elf.split()])) for idx,elf in enumerate(elves)]
    best = max(elf_cals, key=lambda e: e[1])
    return best

if __name__=="__main__":
    max_cal = max_group(sys.argv[1])
    print(max_cal)
    max_cal_3 = max_queue(sys.argv[1], n=3)
    print(sum(max_cal_3))
    # max_idx, max_cal = gather(sys.argv[1])
    # print(max_idx, max_cal)
