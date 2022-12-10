import sys

def move_rope(lines):
    moves = {"R": (0,1), "L": (0,-1), "U": (1,0), "D": (-1,0)}
    h = (0,0)
    t = (0,0)
    past = [t]
    for line in lines:
        direction, n = line.strip().split()
        for i in range(int(n)):
            # move head
            move = moves[direction]
            h = (h[0]+move[0], h[1]+move[1])
            # move tail, if needed
            if abs(h[0]-t[0]) > 1:
                t = (int((h[0]+t[0])/2), h[1])
            elif abs(h[1]-t[1]) > 1:
                t = (h[0], int((h[1]+t[1])/2))
            past.append(t)
    # print_past(past)
    return past

def move_n_rope(lines, n):
    moves = {"R": (0,1), "L": (0,-1), "U": (1,0), "D": (-1,0)}
    rope = [(0,0)]*n
    past = [rope[-1]]
    for lidx, line in enumerate(lines):
        direction, n = line.strip().split()
        for i in range(int(n)):
            # move head
            move = moves[direction]
            rope[0] = (rope[0][0]+move[0], rope[0][1]+move[1])
            # move tail, if needed
            for j in range(1,len(rope)):
                prev = rope[j-1]
                cur = rope[j]
                u0 = abs(prev[0]-cur[0])
                u1 = abs(prev[1]-cur[1])                    
                if u0 > 1 and u1 <= 1:
                    cur = int((prev[0]+cur[0])/2), prev[1]
                elif u0 <= 1 and u1 > 1:
                    cur = prev[0], int((prev[1]+cur[1])/2)
                elif u0 > 1 and u1 > 1:
                    cur = int((prev[0]+cur[0])/2), int((prev[1]+cur[1])/2)
                rope[j] = (cur[0],cur[1])
            past.append(rope[-1])
    # print_past(past)
    return past

def print_past(positions):
    print(positions)
    min_x = min(positions, key=lambda x: x[0])[0]
    max_x = max(positions, key=lambda x: x[0])[0]
    min_y = min(positions, key=lambda x: x[1])[1]
    max_y = max(positions, key=lambda x: x[1])[1]
    for i in range(min_x, max_x+1):
        print("")
        for j in range(min_y, max_y+1):
            if i == 0 and j == 0:
                print("s", end='')
            elif (i,j) in positions:
                print("#", end='')
            else:
                print(".", end='')
    print("\n")

def print_state(rope):
    for i in range(-5, 10):
        # if i == -20:
        #     print("  " + "".join([f"{idx}" for idx in range(-20,20)]))
        #     continue
        print("")
        for j in range(-5, 15):
            if j == -20:
                print(f"{i:>3}", end='')
            elif i == 0 and j == 0:
                print("s", end='')
            elif (i,j) in rope:
                idx = rope.index((i,j))
                if idx == 0: idx = "H"
                print(f"{idx}", end='')
            else:
                print(".", end='')
    print("\n")

def q1(lines):
    past = move_rope(lines)
    return len(set(past))

def q2(lines):
    past = move_n_rope(lines, 10)
    return len(set(past))

if __name__=="__main__":
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    n_pos = q1(lines)
    print(f"# of tail positions with length-2 rope: {n_pos}")
    n_pos_n = q2(lines)
    print(f"# of tail positions with length-10 rope: {n_pos_n}")
            