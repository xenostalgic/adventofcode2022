import sys

def x_by_cycle(lines):
    vals = [1, 1]
    for line in lines:
        if line.strip() == "noop":
            vals += [vals[-1]]
        elif line.startswith("addx"):
            k = int(line.strip().split()[1])
            vals += [vals[-1]]
            vals += [vals[-1]+k]
    return vals

def q1(vals):
    i = 20
    s = 0
    interest = []
    while i < 221:
        s += i*vals[i]
        interest.append(i*vals[i])
        i += 40
    print(interest)
    print(f"Sum of signal strengths: {s}")

def q2(vals):
    for i,v in enumerate(vals[1:]):
        c = i%40
        if c == 0:
            print("")
        if c in range(v-1, v+2):
            print("#", end='')
        else:
            print(".", end='')
    print("")

if __name__=="__main__":
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    vals = x_by_cycle(lines)
    q1(vals)
    q2(vals)


