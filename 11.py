import sys

debug = False

def get_operation(string):
    def op(old):
        new = eval(string)
        return new
    return op

def run_sim(monkeys, n, worry_management="divide"):
    for round in range(n):
        monkey_order = sorted(list(monkeys.keys()))
        for midx in monkey_order:
            for i,worry in enumerate(monkeys[midx]["items"]):
                worry = monkeys[midx]["operation"](worry)
                if worry_management == "divide":
                    worry = int(worry/3)
                else:
                    worry = worry % monkeys[midx]["factor"]
                if worry % monkeys[midx]["test"] == 0:
                    tgt_midx = monkeys[midx]["true"]
                else:
                    tgt_midx = monkeys[midx]["false"]
                monkeys[tgt_midx]["items"].append(worry)
                monkeys[midx]["n_inspections"] += 1
            monkeys[midx]["items"] = []
        if debug and (round+1 in [1,20,1000,2000]):
            print(f"After round {round+1}:")
            inspection_status(monkeys)
    return monkeys

def parse_monkeys(input):
    chunks = input.split("\n\n")
    monkeys = {}
    factor = 1
    for chunk in chunks:
        lines = chunk.split("\n")
        items = map(int, lines[1].strip()[16:].split(", "))
        op_string = " ".join(lines[2].strip().split()[3:])
        test_div = int(lines[3].strip().split()[-1])
        midx = int(lines[0].strip().split()[-1].strip(":"))
        monkey = {
            "items": list(items),
            "operation": get_operation(op_string),
            "test": test_div,
            "true": int(lines[4].strip().split()[-1]),
            "false": int(lines[5].strip().split()[-1]),
            "n_inspections": 0,
        }
        factor = factor * test_div
        monkeys[midx] = monkey
    for midx in monkeys:
        monkeys[midx]["factor"] = factor
    return monkeys

def inspection_status(monkeys):
    for midx in sorted(monkeys):
        c = monkeys[midx]["n_inspections"]
        print(f"Monkey {midx} inspected items {c} times")
    print("")

def q1(monkeys):
    monkeys = run_sim(monkeys, n=20)
    inspection_status(monkeys)
    active = sorted([monkeys[midx]["n_inspections"] for midx in monkeys])
    p = active[-2]*active[-1]
    print(f"Monkey business: {active[-2]}*{active[-1]}={p}\n")

def q2(monkeys):
    monkeys = run_sim(monkeys, n=10000, worry_management="mod_factor")
    inspection_status(monkeys)
    active = sorted([monkeys[midx]["n_inspections"] for midx in monkeys])
    p = active[-2]*active[-1]
    print(f"Monkey business: {active[-2]}*{active[-1]}={p}\n")

if __name__=="__main__":
    with open(sys.argv[1]) as f:
        input = f.read()
    monkeys = parse_monkeys(input)
    q1(monkeys)
    monkeys = parse_monkeys(input)
    q2(monkeys)
