import sys
from collections import defaultdict

import IPython as ipy

OPS = {
    "+": lambda x1, x2: x1+x2,
    "-": lambda x1, x2: x1-x2,
    "*": lambda x1, x2: x1*x2,
    "/": lambda x1, x2: x1/x2,
}

INV = {
    "+": "-",
    "-": "+",
    "*": "/",
    "/": "*",
}

CACHE = {}

def tree_expand(monks):
    def expand(name):
        job = monks[name]
        if len(job) == 1:
            return job[0]
        out = CACHE.get(name)
        if out is not None:
            return out
        op, ch1, ch2 = job
        v1, v2 = expand(ch1), expand(ch2)
        res = OPS[op](v1,v2)
        CACHE[name] = res
        return res
    return expand("root")

def inverse_expand(monks):
    def expand(name):
        if name == "humn":
            return (name, [])
        job = monks[name]
        if len(job) == 1:
            return (job[0], None)
        op, ch1, ch2 = job
        v1, v2 = expand(ch1), expand(ch2)
        if name == "root":
            if v1[1] is None:
                expr, ops, eq_val = v2[0], v2[1], v1[0]
                return expr, ops, eq_val
            else:
                expr, ops, eq_val = v1[0], v1[1], v2[0]
                return expr, ops, eq_val
        if v1[1] is not None:
            # v1 is the humn expression
            res = (f"({v1[0]} {op} {v2[0]})", v1[1] + [(op,v2[0])])
        elif v2[1] is not None:
            # v2 is the humn expression
            res = (f"({v1[0]} {op} {v2[0]})", v2[1] + [(v1[0],op)])
        else:
            res = (OPS[op](v1[0],v2[0]), None)
        return res
    expr, ops, comp_val = expand("root")
    print(expr, "=", comp_val)
    for op_pair in ops[::-1]:
        if op_pair[0] in OPS:
            op, val = op_pair
            val_first = False
        else:
            val, op = op_pair
            val_first = True
        if op in ["*", "+"]:
            new_op = INV[op]
            print(f"X {op} {val:0.0f} = {comp_val:0.0f} -> X = {comp_val:0.0f} {INV[op]} {val:0.0f}")
            comp_val = OPS[INV[op]](comp_val,val)
        elif val_first and op == "/":
            # a/x=b -> x=a/b
            print(f"{val:0.0f} {op} X = {comp_val:0.0f} -> X = {comp_val:0.0f} {op} {val:0.0f}")
            comp_val = val/comp_val
        elif val_first and op == "-":
            #a-x=b -> x=a-b
            print(f"{val:0.0f} {op} X = {comp_val:0.0f} -> X = {comp_val:0.0f} {op} {val:0.0f}")
            comp_val = val-comp_val
        else:
            # x/a=b -> x=b*a; x-a=b -> x=b+a
            print(f"{val:0.0f} {op} X = {comp_val:0.0f} -> X = {comp_val:0.0f} {INV[op]} {val:0.0f}")
            comp_val = OPS[INV[op]](comp_val,val)
    if comp_val != int(comp_val):
        print("Result is not an integer: {comp_val:.2f}")
    return int(comp_val)

def read_input(filename):
    monks = {}
    for line in open(filename, "r"):
        ls = line.strip().split()
        name = ls[0].strip(":")
        if len(ls) == 2:
            monks[name] = (int(ls[1]),)
        else:
            m1, op, m2 = ls[1:]
            monks[name] = (op, m1, m2)
    return monks

if __name__=="__main__":
    monks = read_input(sys.argv[1])
    print("== Part 1 ==")
    result = tree_expand(monks)
    print("Result:", result)
    print("== Part 2 ==")
    soln = inverse_expand(monks)
    print("Solution:", soln)