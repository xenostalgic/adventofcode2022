import sys

def visible_grid(lines):
    visible_count = 0
    for i, row in enumerate(lines):
        for j, tree in enumerate(row):
            if i == 0 or i == len(lines)-1:
                visible_count += 1
            elif j == 0 or j == len(row)-1:
                visible_count += 1
            elif tree > max(row[:j]) or tree > max(row[j+1:]):
                visible_count += 1
            else:
                col = [l[j] for l in lines]
                if tree > max(col[:i]) or tree > max(col[i+1:]):
                    visible_count += 1
    return visible_count

def scenic_score(lines):
    max_score = 0
    for i, row in enumerate(lines):
        for j, tree in enumerate(row):
            uscore, dscore, lscore, rscore = 0, 0, 0, 0
            k = i-1
            while k >= 0:
                uscore += 1
                if not lines[k][j] < tree:
                    break
                k -= 1
            k = i+1
            while k < len(lines):
                dscore += 1
                if not lines[k][j] < tree:
                    break
                k += 1
            k = j-1
            while k >= 0:
                lscore += 1
                if not lines[i][k] < tree:
                    break
                k -= 1
            k = j+1
            while k < len(row):
                rscore += 1
                if not lines[i][k] < tree:
                    break
                k += 1
            scenic_score = uscore*dscore*lscore*rscore
            if scenic_score > max_score:
                print(f"Updating max score to {scenic_score} for tree with height {tree} at ({i},{j})")
                print(f"Scores: {uscore}, {dscore}, {lscore}, {rscore}")
                max_score = scenic_score
    return max_score

if __name__=="__main__":
    with open(sys.argv[1]) as f:
        lines = [l.strip() for l in f.readlines()]
    print("Visible trees:", visible_grid(lines))
    print("Max scenic score:", scenic_score(lines))

