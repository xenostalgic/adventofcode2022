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

    dists = {pair:weight for pair,weight in weights.items() if pair[0] in targets and pair[1] in targets}
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

def comp_from_key(nodes, key):
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
    flow_vals = np.array([flows[n] for n in nodes])

    k = len(nodes)
    n = 2**k # all subsets of valves
    print("Precaching subset indices...")
    skeys = [format(i, '016b')[::-1] for i in range(n)]
    sbits = [int("0b"+skey,2) for skey in skeys]
    subsets = [subset_from_key(nodes,key) for key in skeys]
    subidxs = {sidx:[nodes.index(n) for n in subset] for sidx,subset in enumerate(subsets)}

    print("Precaching subset complements...")
    scomp_sets = [comp_from_key(nodes,skey) for sidx,skey in enumerate(skeys)]
    scomp_sidxs = [subsets.index(subset) for sidx,subset in enumerate(scomp_sets)]
    sflows = {
        sidx: sum([
            flows[node] for node in subsets[sidx]
        ]) 
        for sidx in range(n)
    }
    paths = defaultdict(list)

    # get adjacent valve states
    subsq_adj = defaultdict(set)
    prior_adj = defaultdict(set)
    print("Precaching subset adjacencies...")
    for sidx,skey in tqdm(enumerate(skeys), total=n):
        for nidx in range(k):
            if skey[nidx] == "1":
                prev_idx = sidx - (2**nidx)
                prior_adj[sidx].add(prev_idx)
                subsq_adj[prev_idx].add(sidx)
            else:
                next_idx = sidx + (2**nidx)
                subsq_adj[sidx].add(next_idx)
                prior_adj[next_idx].add(sidx)
        subsq_adj[sidx].add(sidx)
        prior_adj[sidx].add(sidx)
    subsq_adj = {k:list(v) for k,v in subsq_adj.items()}
    prior_adj = {k:list(v) for k,v in prior_adj.items()}

    # # get inverse of each subset
    # complement = defaultdict(list)
    # for sidx,skey in tqdm(enumerate(skeys), total=n):
    #     ckey = "".join(["0" if ch=="1" else "1" for ch in skey])
    #     complement[sidx] = skeys.index(ckey)

    lattice = np.zeros((time+1,n,k),dtype=np.int16) # time x subsets x position
    lattice -= 1
    start_idx = nodes.index("AA")
    lattice[0,0,start_idx] = 0 # can start at time = 0, no valves, at node AA - but nowhere else!
    paths[(0,0,start_idx)] = ["start at AA"]

    max_flow = 1
    for f in sorted(flows.values())[1:]:
        if f > 0:
            max_flow += f
    max_dist = max(dists.values())
    print(f"N={n}, k={k}, t={time}; max_flow={max_flow}, max_dist={max_dist}")

    best_so_far = -1
    best_sidx_so_far = -1
    for t in tqdm(range(1,time+1)):
        lattice[t,:,:] = lattice[t-1,:,:]
        valid_idx = np.argwhere(lattice[t,:,:]>-1)
        valid_next = []
        for (sidx,pos) in valid_idx:
            valid_next += subsq_adj[sidx] 
        valid_next = list(set(valid_next))
        # print("valid next states:", valid_next)
        # ipy.embed()
        for sidx in valid_next:
            valid_prev = np.argwhere(lattice[t,prior_adj[sidx],:] > -1)
            if len(valid_prev) == 0: # none of these states are reachable
                continue
            if len(subsets[sidx]) > t*2:
                continue

            # if best_so_far > -1:
            #     # best_sidx_so_far
            #     if lattice[t-1,sidx,:].max() < best_so_far - max_flow*(time-t):
            #         # no way to catch up now
            #         lattice[t-1,sidx,:] = -1
            #         continue
            
            # if sidx is a strict subset of the best state and the score difference is more than max_flow, can't get better
            # if (sidx & best_sidx_so_far == sidx) and (lattice[t-1,sidx,:].max() < best_so_far - max_flow):
            #     lattice[t,sidx,:] = -1
            #     continue

            for pos_idx, pos_node in enumerate(nodes):
                # worst case, just sit still for one tick
                best_prev_idx = (t-1,sidx,pos_idx)
                best_prev_score = lattice[best_prev_idx]
                best_action = "??? to"
                if best_prev_score != -1:
                    best_prev_score += sflows[sidx]
                    best_action = "wait at"
                # if this valve is open, we could have opened it between t-1 and t
                if pos_idx in subidxs[sidx]: #if skeys[sidx][pos_idx] == "1":
                    prev_key = list(skeys[sidx])
                    prev_key[pos_idx] = "0"
                    prev_key = "".join(prev_key)
                    sidx_prev = skeys.index(prev_key)
                    prev_score = lattice[t-1,sidx_prev,pos_idx]
                    if prev_score != -1:
                        prev_score += sflows[sidx_prev]
                        if prev_score >= best_prev_score:
                            best_prev_score = prev_score
                            best_prev_idx = (t-1,sidx_prev,pos_idx)
                            best_action = "turn valve at"
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
                        best_action = f"move {d} to"

                lattice[t,sidx,pos_idx] = best_prev_score
                # if lattice[t,sidx,pos_idx] == lattice[t-1,sidx,pos_idx]:
                #     # waiting is guaranteed nonoptimal
                #     lattice[t,sidx,pos_idx] = -1
                paths[(t,sidx,pos_idx)] = paths[best_prev_idx] + [best_action + " " + pos_node]

        best_so_far = lattice[t,:,:].max()
        best_sidx_so_far = np.argwhere(lattice==best_so_far)[0][1]
        print(f"Minute {t}: best score = {best_so_far}")
        if best_so_far < 0:
            ipy.embed()

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

def q2(filename):
    pass

if __name__=="__main__":
    print("\n== Part 1 ==")
    q1(sys.argv[1])
    print("\n== Part 2 ==")
    q2(sys.argv[1])
