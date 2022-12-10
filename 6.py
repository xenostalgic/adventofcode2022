import sys

import IPython as ipy

def detect_n(stream, n=4):
    for i in range(len(stream)):
        if len(set(stream[i-(n-1):i+1])) == n:
            print(stream[i-(n-1):i+1])
            return i+1
    return None

if __name__=="__main__":
    with open(sys.argv[1]) as f:
        input = f.read()
    print(detect_n(input, n=4))
    print(detect_n(input, n=14))