import sys
from collections import defaultdict
from enum import Enum
from functools import cmp_to_key

debug=False

class Ordered(Enum):
    INORDER = -1
    OUTORDER = 1
    UNDECIDED = 0


def compare_wrap(item1, item2):
    return compare(item1, item2).value


def compare(left, right, indent=""):
    if debug: print(indent + f"Compare {left} vs {right}")
    if left == right:
        return Ordered.UNDECIDED
    if isinstance(left, int) and isinstance(right, int):
        if left < right:
            if debug: print(indent + "  " + f"Left side is smaller so inputs are in the right order")
            return Ordered.INORDER
        elif left > right:
            if debug: print(indent + "  " + f"Right side is smaller so inputs are NOT in the right order")
            return Ordered.OUTORDER
        else:
            return Ordered.UNDECIDED
    elif isinstance(left, list) and isinstance(right, list):
        if len(right) == 0:
            if debug: print(indent + "  " + f"Right side ran out of items, so inputs are NOT in the right order")
            return Ordered.OUTORDER
        if len(left) == 0:
            if debug: print(indent + "  " + f"Left side ran out of items, so inputs are in the right order")
            return Ordered.INORDER
        for i in range(max(len(left), len(right))):
            if i >= len(left):
                if debug: print(indent + "  " + f"Left side ran out of items, so inputs are in the right order")
                return Ordered.INORDER
            if i >= len(right):
                if debug: print(indent + "  " + f"Right side ran out of items, so inputs are NOT in the right order")
                return Ordered.OUTORDER
            cur = compare(left[i], right[i], indent=indent+"  ")
            if cur == Ordered.INORDER or cur == Ordered.OUTORDER:
                return cur
        return Ordered.UNDECIDED
    else:
        if isinstance(left, int):
            return compare([left], right, indent=indent+"  ")
        elif isinstance(right, int):
            return compare(left, [right], indent=indent+"  ")
    print(indent + f"fail case for inputs {left}, {right}")


def read_input_pairs(filename):
    with open(filename, "r") as f:
        chunks = f.read().split("\n\n") # read chunks
    pairs = [tuple([eval(line) for line in chunk.splitlines()]) for chunk in chunks]
    return pairs


def read_input_list(filename):
    with open(filename, "r") as f:
        packets = [eval(line.strip()) for line in f.readlines() if len(line.strip()) > 0]
    return packets


def q1(filename):
    pairs = read_input_pairs(filename)
    ordered = []
    for i, pair in enumerate(pairs):
        if debug: print(f"\n== Pair {i+1} ==")
        c = compare(pair[0], pair[1])
        if c == Ordered.INORDER:
            # print(f"Pair {i} was in the right order\n")
            ordered.append(i+1)
        elif c == Ordered.UNDECIDED:
            if debug: print(f"pair {i} was undecided: {pair}\n")
        else:
            # print(f"Pair {i} was NOT in the right order\n")
            pass
    print(ordered)
    print(sum(ordered))


def q2(filename):
    packets = read_input_list(filename)
    packets += [[[2]], [[6]]]
    sorted_packets = sorted(packets, key=cmp_to_key(compare_wrap))
    decoder = []
    for i,packet in enumerate(sorted_packets):
        if packet == [[2]] or packet == [[6]]:
            decoder.append(i+1)
    key = decoder[0]*decoder[1]
    print(f"Decoder keys {decoder[0]}, {decoder[1]}: {key}")


if __name__=="__main__":
    q1(sys.argv[1])
    q2(sys.argv[1])