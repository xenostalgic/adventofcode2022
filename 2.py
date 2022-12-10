import sys

def score(m1, m2):
    readable = ["rock", "paper", "scissors"][m1], ["rock", "paper", "scissors"][m2]
    if m2-m1 in [1,-2]:
        s = 6
        print(readable[1], "beats", readable[0])
    elif m2-m1 == 0:
        s = 3
        print(readable[1], "ties with", readable[0])
    else: # if m2-m1 in [2,-1]
        s = 0
        print(readable[1], "loses to", readable[0])
    print(s+m2+1)
    return s + m2+1

def score2(move, outcome):
    if outcome == 0: # loss
        target = (move-1) % 3
        readable = ["rock", "paper", "scissors"][move], ["rock", "paper", "scissors"][target]
        print(f"To lose, play {readable[1]} vs {readable[0]}")
        score = 0 + target+1
    elif outcome == 1: # draw
        target = move
        readable = ["rock", "paper", "scissors"][move], ["rock", "paper", "scissors"][target]
        print(f"To draw, play {readable[1]} vs {readable[0]}")
        score = 3 + target+1
    elif outcome == 2: # win
        target = (move+1) % 3
        readable = ["rock", "paper", "scissors"][move], ["rock", "paper", "scissors"][target]
        print(f"To win, play {readable[1]} vs {readable[0]} ({target} vs {move})")
        score = 6 + target+1
    print(score)
    return score

def rps_guide(filename, target=True):
    total = 0
    for line in open(filename, "r"):
        a, b = line.strip().split()
        if target:
            m1 = "ABC".index(a)
            m2 = "XYZ".index(b)
            total += score(m1,m2)
        else:
            move = "ABC".index(a)
            outcome = "XYZ".index(b)
            total += score2(move, outcome)
    return total

if __name__=="__main__":
    total_score = rps_guide(sys.argv[1])
    alt_score = rps_guide(sys.argv[1], target=False)
    print("total:", total_score)
    print("alt:", alt_score)
