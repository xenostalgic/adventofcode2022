import sys
import numpy as np
from collections import defaultdict
from math import log
import itertools
from tqdm import tqdm

import IPython as ipy

def get_min_dists(targets, edges):
    # compute distances using N iterations of Dijkstra's algorithm
    max_dist = len(edges)
    weights = {}
    for v1 in edges:
        weights[(v1,v1)] = 0
        for v2 in edges[v1]:
            weights[(v1,v2)] = 1
            weights[(v2,v1)] = 1
    for v1 in targets:
        unvisited = set([v2 for v2 in edges])
        # tentative = {v2:weights[(v1,v2)] if (v1,v2) in weights else (n*n) for v2 in unvisited}
        tentative = {v2:(max_dist**3) for v2 in unvisited}
        tentative[v1] = 0
        cur_node = v1
        while len(unvisited) > 0:
            for neighbor in edges[cur_node]:
                if neighbor not in unvisited:
                    continue
                via_weight = tentative[cur_node] + weights[(cur_node,neighbor)]
                if via_weight < tentative[neighbor]:
                    tentative[neighbor] = via_weight
            unvisited.remove(cur_node)
            if len(unvisited) == 0:
                break
            cur_node = min(unvisited, key=tentative.get)
        for v2 in tentative:
            edges[v1].add(v2)
            edges[v2].add(v1)
            if (v1,v2) in weights and (weights[(v1,v2)] < tentative[v2]):
                print("found nonminimum weight")
                ipy.embed()
            weights[(v1,v2)] = tentative[v2]
            weights[(v2,v1)] = tentative[v2]

    # find number of fake nodes needed to make a power of 2
    x = len(targets)
    n = 2**(int(log(x-1,2))+1)

    # # dists as numpy array
    # dists = np.zeros((n,n))-1
    # for i,v1 in enumerate(targets):
    #     for j,v2 in enumerate(targets):
    #         dists[i,j] = weights[(v1,v2)]
    # for i in range(x,n):
    #     # spare nodes are connected but far from everything
    #     dists[i,:] = len(edges)
    #     dists[:,i] = len(edges)

    # dists as Dict[tuple,int]
    dists = {pair:weight for pair,weight in weights.items() if pair[0] in targets and pair[1] in targets}
    # for i in range(x,n):
    #     # add fake nodes
    #     fake_i = f"FAKE_{i}"
    #     src = targets[0]
    #     for valve in targets:
    #         d = dists[(valve,src)] + max_dist
    #         dists[(valve,fake_i)] = d
    #         dists[(fake_i,valve)] = d
    #     for j in range(x,n):
    #         fake_j = f"FAKE_{j}"
    #         if j == i:
    #             dists[(fake_i,fake_j)] = 0
    #             dists[(fake_j,fake_i)] = 0
    #         else:
    #             dists[(fake_i,fake_j)] = max_dist*2
    #             dists[(fake_j,fake_i)] = max_dist*2
    return dists


def read_input(filename, floor=False):
    with open(filename, "r") as f:
        lines = [l.strip() for l in f.readlines()]
    flows = {}
    edges = defaultdict(set)
    # get full graph + flow rates
    for line in lines:
        toks = line.split()
        v1 = toks[1]
        flow_rate = int(toks[4].strip(";").split("=")[-1])
        neighbors = [tok.strip(",") for tok in toks[9:]]
        flows[v1] = flow_rate
        for v2 in neighbors:
            edges[v1].add(v2)
            edges[v2].add(v1)
    flows = {valve:flow for valve, flow in flows.items() if flow != 0 or valve == "AA"}
    targets = [v for v in flows]
    mut_edges = {k:v.copy() for k,v in edges.items()}
    dists = get_min_dists(targets, mut_edges)
    # add fake nodes to flows
    for p in dists:
        if p[0] not in flows:
            flows[p[0]] = 0
    return flows, dists

def subset_from_key(nodes, key):
    subset = []
    for i,ch in enumerate(key):
        if ch == "1":
            subset.append(nodes[i])
    return sorted(subset)

def key_from_subset(nodes, subset):
    key = ["0"]*16
    for node in subset:
        key[nodes.index(node)] = "1"
    return "".join(key)

def dynamic_progress(flows, dists, time=30):
    nodes = sorted(list(flows.keys()))
    k = len(nodes)
    n = 2**k # all subsets of valves
    skeys = [format(i, '016b')[::-1] for i in range(n)]
    subsets = [subset_from_key(nodes,key) for key in skeys]
    sflows = {
        sidx: sum([
            flows[node] for node in subsets[sidx]
        ]) 
        for sidx in range(n)
    }
    paths = defaultdict(list)

    lattice = np.zeros((time+1,n,k),dtype=np.int16) # time x subsets x position
    lattice -= 1
    start_idx = nodes.index("AA")
    lattice[0,0,start_idx] = 0 # can start at time = 0, no valves, at node AA - but nowhere else!
    paths[(0,0,start_idx)] = ["start at AA"]

    max_flow = max(flows.values())
    max_dist = max(dists.values())
    print(f"N={n}, k={k}, t={time}; max_flow={max_flow}, max_dist={max_dist}")

    best_so_far = -1
    for t in range(1,time+1):
        lattice[t,:,:] = lattice[t-1,:,:]
        for sidx in tqdm(range(n)):
            if len(subsets[sidx]) > t*2:
                continue
            # if lattice[t-1,sidx,:].max() < best_so_far - (max_flow*max_dist):
            #     continue
            for pos_idx, pos_node in enumerate(nodes):
                # worst case, just sit still for one tick
                best_prev_score = lattice[t-1,sidx,pos_idx]
                if best_prev_score != -1:
                    best_prev_score += sflows[sidx]
                # best_action = "wait at"
                # if this valve is open, we could have opened it between t-1 and t
                if skeys[sidx][pos_idx] == "1":
                    prev_key = list(skeys[sidx])
                    prev_key[pos_idx] = "0"
                    prev_key = "".join(prev_key)
                    sidx_prev = skeys.index(prev_key)
                    prev_score = lattice[t-1,sidx_prev,pos_idx]
                    if prev_score != -1:
                        prev_score += sflows[sidx_prev]
                        if prev_score >= best_prev_score:
                            best_prev_score = prev_score
                            # best_prev_idx = (t-1,sidx_prev,pos_idx)
                        # best_action = "turn valve at"
                # or, could have traveled from another node without changing valve state
                for prev_idx, prev_node in enumerate(nodes):
                    # max over previous positions
                    d = dists[(pos_node,prev_node)]
                    if t-d < 0 or lattice[t-d,sidx,prev_idx] == -1:
                        continue
                    # could have come from prev_node
                    prev_score = lattice[t-d,sidx,prev_idx] + d*sflows[sidx]
                    if prev_score >= best_prev_score:
                        best_prev_score = prev_score
                        best_prev_idx = (t-d,sidx,prev_idx)
                        # best_action = f"move {d} to"

                lattice[t,sidx,pos_idx] = best_prev_score
                if lattice[t,sidx,pos_idx] == lattice[t-1,sidx,pos_idx]:
                    # waiting is guaranteed nonoptimal
                    lattice[t,sidx,pos_idx] = -1
                # paths[(t,sidx,pos_idx)] = paths[best_prev_idx] + [best_action + " " + pos_node]

        best_so_far = lattice[t,:,:].max()
        print(f"Minute {t}: best score = {best_so_far}")

    best_score = lattice[-1,:,:].max()
    best_idx = tuple(ax[0] for ax in np.where(lattice==best_score))
    print("")
    print("Best path:", paths[best_idx])
    print("Best score:", best_score)
    return lattice[-1,:,:].max()

def q1(filename):
    flows, dists = read_input(filename)
    max_flow = dynamic_progress(flows, dists)
    print("Max flow:", max_flow)
    ipy.embed()

def q2(filename):
    pass

if __name__=="__main__":
    print("\n== Part 1 ==")
    q1(sys.argv[1])
    print("\n== Part 2 ==")
    q2(sys.argv[1])
