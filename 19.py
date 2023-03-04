import sys
import numpy

import IPython as ipy

RES_LIST = ["ore", "clay", "obsidian", "geode"]

"""
dynamic programming again? 4 types of robots, 3 types of resources, each with some count... --> score?
actually not sure if dynamic programming is right. some kind of search?

for each resource, there is some robot type that costs the most of that resource.
once you are getting that many per tick, there is no point getting more.
so you can trim the state space by setting a max number of each robot type

also:
- on the last tick, no point in buying robots
- on tick n-1, no point in buying robots except geode robots
- on tick n-2, no point in buying robots except geode/obsidian robots
- on tick n-3, no point in buying robots except geode/obsidian/clay robots
can you generalize this more?
"""

def read_input(filename):
    blueprints = []
    for line in open(filename):
        entries = line.lower().strip().split("each")[1:]
        pairs = [e.strip().split(" costs ") for e in entries]
        type_costs = {res:0 for res in RES_LIST}
        for rtype,cost in pairs:
            rcosts = cost.strip(".").split(" and ")
            rcosts = {c.split()[1]:int(c.split()[0]) for c in rcosts}
            type_costs[rtype] = rcosts
        blueprints.append(type_costs)
    return blueprints

def can_build(cur_state, rtype, blueprint):
    for ctype,count in blueprint[rtype].items():
        if cur_state["resources"][ctype] < count:
            return False
    return True

def max_geodes(blueprint):
    resources = {"ore":0, "clay":0, "obsidian":0, "geode":0}
    rates = {"ore":0, "clay":0, "obsidian":0, "geode":0}
    maxes = {res:int(24 / blueprint[f"{res} robot"]["ore"])+1 for res in resources}
    # (resources, rates)
    cur_state = {"best_time": 0, "resources":resources, "rates":rates}
    # sort of like Dijkstra's algorithm, with neighbors calculated on-the-fly?
    while True:
        # get neighbors
        neighbors = []
        if cur_state["best_time"] >= 24:
            raise NotImplementedError("need to handle finish")
            pass
        for rtype in blueprint:
            if not can_build(cur_state,rtype,blueprint):
                continue
            neighbor = {
                "resources":{res:count-blueprint[rtype][res] for res,count in cur_state["resources"]},
                "rates":{res:rate for res,rate in cur_state["rates"]}
            }
            neighbor["rates"][rtype.split()[0]] += 1
        



if __name__=="__main__":
    blueprints = read_input(sys.argv[1])
    print("== Part 1 ==")
    qualities = []
    for i,bp in enumerate(blueprints):
        score = max_geodes(bp)
        quality = (i+1)*score
        qualities.append(quality)
    print("Sum of quality levels:", sum(qualities))