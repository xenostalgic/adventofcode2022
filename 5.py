import sys
import IPython as ipy

def print_diagram(stacks):
    for col in sorted(stacks.keys()):
        print(f"{col} | " + " ".join(stacks[col]))
    print("--------")

def parse_diagram(lines):
    cols = [idx for idx in lines[-1].split()]
    stacks = {col:[] for col in cols}
    for line in lines[-2::-1]:
        for col_idx in range(len(cols)):
            col_val = line[(col_idx*4)+1:(col_idx*4)+2]
            if len(col_val.strip()) == 0:
                continue
            stacks[cols[col_idx]].append(col_val)
    return cols, stacks

def rearrange(stacks, instructions, over_9000=False):
    for ins in instructions:
        # print("Before:")
        # print_diagram(stacks)
        n, src, tgt = ins
        n = int(n)
        # ipy.embed()
        moved = stacks[src][-n:]
        if over_9000:
            stacks[tgt] += moved
        else:
            stacks[tgt] += moved[::-1]
        stacks[src] = stacks[src][:-n]
        # print(f"After moving {n} from {src} to {tgt}:")
        # print_diagram(stacks)
    return stacks

def parse_input(filename):
    diagram = []
    instructions = []
    diagram_done = False
    for line in open(filename, "r"):
        line = line.strip("\n")
        if len(line.strip()) == 0:
            diagram_done = True
        elif diagram_done:
            ins = line.split()
            ins = (ins[1], ins[3], ins[5])
            instructions.append(ins)
        else:
            diagram.append(line)
    return diagram, instructions

def q1(diagram, instructions):
    cols, stacks = parse_diagram(diagram)
    stacks = rearrange(stacks, instructions)
    tops = [stacks[col][-1] for col in cols]
    print("Q1:", "".join(tops))

def q2(diagram, instructions):
    cols, stacks = parse_diagram(diagram)
    stacks = rearrange(stacks, instructions, over_9000=True)
    tops = [stacks[col][-1] for col in cols]
    print("Q2:", "".join(tops))

if __name__=="__main__":
    diagram, instructions = parse_input(sys.argv[1])
    q1(diagram, instructions)
    q2(diagram, instructions)
