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
    flows = {valve:flow for valve, flow in flows.items()}
    targets = [v for v in flows if flows[v] > 0 or v == "AA"]
    mut_edges = {k:v.copy() for k,v in edges.items()}
    dists = get_min_dists(targets, mut_edges)
    return flows, edges, dists

def subset_from_key(nodes, key):
    subset = []
    for i,ch in enumerate(key):
        if ch == "1":
            subset.append(nodes[-i-1]) # reverse index, so idx 0 corresponds to the "end" of the key
    return sorted(subset)

def key_from_subset(nodes, subset):
    key = ["0"]*16
    for node in subset:
        key[nodes.index(node)] = "1"
    return "".join(key)

def dynamic_progress(flows, dists, time=30):
    start_node = "AA"
    flows = {node:flow for node,flow in flows.items() if node==start_node or flow > 0}
    pos_nodes = sorted(list(flows.keys()))
    start_pidx = pos_nodes.index(start_node)
    vlv_nodes = [n for n in pos_nodes if n != start_node]

    p = len(pos_nodes)
    k = len(vlv_nodes)
    n = 2**k # all subsets of valves
    print("Precaching subset indices...")
    skeys = [format(i, f"0{k}b") for i in range(n)]
    subsets = [subset_from_key(vlv_nodes, key) for key in skeys]
    subidxs = {sidx:[vlv_nodes.index(n) for n in subset] for sidx,subset in enumerate(subsets)}

    sflows = {
        sidx: sum([
            flows[vnode] for vnode in subsets[sidx]
        ]) 
        for sidx in range(n)
    }
    paths = defaultdict(list)

    # get adjacent valve states
    subsq_adj = defaultdict(set)
    prior_adj = defaultdict(set)
    print("Precaching subset adjacencies...")
    for sidx in tqdm(range(n)):
        for vidx in range(k):
            if sidx | (2**vidx) == sidx:
                prev_sidx = sidx - (2**vidx)
                prior_adj[sidx].add(prev_sidx)
                subsq_adj[prev_sidx].add(sidx)
            else:
                next_idx = sidx + (2**vidx)
                subsq_adj[sidx].add(next_idx)
                prior_adj[next_idx].add(sidx)
        subsq_adj[sidx].add(sidx)
        prior_adj[sidx].add(sidx)
    subsq_adj = {sidx:list(ssidxs) for sidx,ssidxs in subsq_adj.items()}
    prior_adj = {sidx:list(psidxs) for sidx,psidxs in prior_adj.items()}

    lattice = np.zeros((time+1,n,k+1),dtype=np.int16) # time x valve subsets x position
    lattice -= 1
    lattice[0,0,start_pidx] = 0 # start at time = 0, no valves, at pnode AA
    paths[(0,0,start_pidx)] = ["start at AA"]

    max_flow = 1
    for f in sorted(flows.values())[1:]:
        if f > 0:
            max_flow += f
    max_dist = max(dists.values())
    print(f"N={n}, k={k}, t={time}; max_flow={max_flow}, max_dist={max_dist}")

    best_so_far = -1
    best_sidx_so_far = -1
    for t in range(1,time+1):
        lattice[t,:,:] = lattice[t-1,:,:]
        valid_idx = np.argwhere(lattice[t,:,:]>-1)
        valid_next = []
        for (sidx,_) in valid_idx:
            valid_next += subsq_adj[sidx] 
        valid_next = list(set(valid_next))
        for sidx in tqdm(valid_next):
            if len(subsets[sidx]) > t*2: # haven't had time to reach these states
                continue

            for pidx, pnode in enumerate(pos_nodes):
                # worst case, just sit still for one tick
                best_prev_idx = (t-1,sidx,pidx)
                best_prev_score = lattice[best_prev_idx]
                best_action = "??? to"
                if best_prev_score != -1:
                    best_prev_score += sflows[sidx]
                    best_action = "wait at"
                # if this valve is open, we could have opened it between t-1 and t without changing pos
                vidx = pidx - 1
                if vidx in subidxs[sidx]:
                    prev_sidx = sidx - (2**vidx)
                    prev_score = lattice[t-1,prev_sidx,pidx]
                    if prev_score != -1:
                        prev_score += sflows[prev_sidx]
                        if prev_score >= best_prev_score:
                            best_prev_score = prev_score
                            best_prev_idx = (t-1,prev_sidx,pidx)
                            best_action = "turn valve at"
                # or, could have traveled from another node without changing valve state
                for prev_pidx, prev_pnode in enumerate(pos_nodes):
                    # max over previous positions
                    d = dists[(pnode,prev_pnode)]
                    if t-d < 0 or lattice[t-d,sidx,prev_pidx] == -1:
                        continue
                    # could have come from prev_node
                    prev_score = lattice[t-d,sidx,prev_pidx] + d*sflows[sidx]
                    if prev_score >= best_prev_score:
                        best_prev_score = prev_score
                        best_prev_idx = (t-d,sidx,prev_pidx)
                        best_action = f"move {d} to"

                lattice[t,sidx,pidx] = best_prev_score
                paths[(t,sidx,pidx)] = paths[best_prev_idx] + [best_action + " " + pnode]

        best_so_far = lattice[t,:,:].max()
        best_indices = np.argwhere(lattice[t,:,:]==best_so_far)
        print(f"Minute {t}: best score = {best_so_far} at paths:")
        #for idx in best_indices:
        #    print(f"valves {subsets[idx[0]]}, node {pos_nodes[idx[1]]}: {paths[(t,idx[0],idx[1])]}")

    best_score = lattice[-1,:,:].max()
    best_idx = tuple(ax[0] for ax in np.where(lattice==best_score))
    print("")
    print("Best path:", paths[best_idx])
    print("Best score:", best_score)
    return lattice[-1,:,:].max()


def dynamic_progress_pair(flows, edges, dists, time):
    start_node = "AA"
    pos_nodes = sorted(list(flows.keys()))
    start_pidx = pos_nodes.index(start_node)
    vlv_nodes = [n for n in pos_nodes if flows[n] > 0]

    vlv_dists = [dists[k] for k in dists if k[0] in vlv_nodes and k[1] in vlv_nodes]
    max_dist = max(vlv_dists)
    avg_dist = np.mean(vlv_dists)

    p = len(pos_nodes)
    k = len(vlv_nodes)
    n = 2**k # all subsets of valves

    print("Precaching position adjacencies...")
    pidx_edges = {
        pos_nodes.index(k_pnode):sorted([pos_nodes.index(v) for v in v_pnodes])
        for k_pnode,v_pnodes in edges.items()
    }
    print("Precaching subset indices...")
    skeys = [format(i, f"0{k}b") for i in range(n)]
    subsets = [subset_from_key(vlv_nodes, key) for key in skeys]
    p2vidx = {
        pidx:(vlv_nodes.index(pnode) if pnode in vlv_nodes else None)
        for pidx,pnode in enumerate(pos_nodes)
    }

    sflows = {
        sidx: sum([
            flows[vnode] for vnode in subsets[sidx]
        ]) 
        for sidx in range(n)
    }
    paths = defaultdict(list)

    # get adjacent valve states
    subsq_adj = defaultdict(set)
    print("Precaching subset adjacencies...")
    for sidx in tqdm(range(n)):
        for vidx_a, vidx_b in itertools.product(range(k), range(k)):
            if vidx_a == vidx_b:
                continue
            adj_sidx = sidx
            adj_sidx += (2**vidx_a) if (sidx | (2**vidx_a) != adj_sidx) else -(2**vidx_a)
            subsq_adj[sidx].add(adj_sidx)
            adj_sidx += (2**vidx_b) if (adj_sidx | (2**vidx_b) != adj_sidx) else -(2**vidx_b)
            subsq_adj[sidx].add(adj_sidx)
            if adj_sidx >= len(subsets) or adj_sidx < 0:
                ipy.embed()
        subsq_adj[sidx].add(sidx)
    subsq_adj = {sidx:list(ssidxs) for sidx,ssidxs in subsq_adj.items()}

    lattice = np.zeros((time+1,n,p,p),dtype=np.int16) # time x valve subsets x position x position
    lattice -= 1
    lattice[0,0,start_pidx,start_pidx] = 0 # start at time = 0, no valves, at pnode AA
    paths[(0,0,start_pidx,start_pidx)] = ["both start at AA"]

    max_flow = 1
    for f in sorted(flows.values())[1:]:
        if f > 0:
            max_flow += f
    print(f"N={n}, k={k}, t={time}; max_flow={max_flow}; max_dist={max_dist}, avg_dist={avg_dist:.3}")

    def print_index(idx):
        print(f"time {idx[0]}, valves {subsets[idx[1]]}, ({pos_nodes[idx[2]]}, {pos_nodes[idx[3]]}): {paths[idx]}")

    # just precompute all position *pair* adjacencies?
    all_prev_indices = defaultdict(list)
    print("Precaching position pair adjacencies...")
    for sidx in tqdm(range(n)):
        for pidx_a, pidx_b in itertools.product(range(p), range(p)):
            idx = sidx,pidx_a,pidx_b
            vidx_a = p2vidx[pidx_a]
            vidx_b = p2vidx[pidx_b]
            # whether current position's valves are open
            vidx_a_present = vidx_a is not None and (sidx | (2**vidx_a) == sidx)
            vidx_b_present = vidx_b is not None and (sidx | (2**vidx_b) == sidx)
            ppos_a = pidx_edges[pidx_a]
            ppos_b = pidx_edges[pidx_b]
            for prev_pidx_a, prev_pidx_b in itertools.product(ppos_a, ppos_b):
                prev_idx = (sidx,prev_pidx_a,prev_pidx_b)
                all_prev_indices[idx].append(prev_idx)
            if vidx_a_present:
                prev_sidx = sidx - (2**vidx_a)
                for prev_pidx_b in ppos_b:
                    prev_idx = (prev_sidx,pidx_a,prev_pidx_b)
                    all_prev_indices[idx].append(prev_idx)
            if vidx_b_present:
                prev_sidx = sidx - (2**vidx_b)
                for prev_pidx_a in ppos_a:
                    prev_idx = (prev_sidx,prev_pidx_a,pidx_b)
                    all_prev_indices[idx].append(prev_idx)
            if vidx_a_present and vidx_b_present and vidx_a != vidx_b:
                prev_sidx = sidx - (2**vidx_a) - (2**vidx_b)
                prev_idx = (prev_sidx,pidx_a,pidx_b)
                all_prev_indices[idx].append(prev_idx)

    best_so_far = -1
    for t in range(1,time+1):
        lattice[t,:,:,:] = lattice[t-1,:,:,:]
        valid_idx = np.argwhere(lattice[t,:,:,:]>-1)
        valid_next = []
        valid_sidices = set([sidx for (sidx,_,_) in valid_idx])
        for sidx in valid_sidices:
            valid_next += subsq_adj[sidx]
        valid_next = set(valid_next)
        # if you can't turn on at least some valves, what are you even doing??
        def min_valves(n_v):
            # not valid in general, but a reasonable heuristic given the connectedness
            if t < max_dist-avg_dist:
                return True
            return n_v >= int((t-max_dist+avg_dist)/(avg_dist+1))
        valid_next = [sidx for sidx in set(valid_next) if min_valves(len(subsets[sidx]))]
        for sidx in tqdm(valid_next):
             # double loop over positions - you and the elephant
            for pidx_a, pidx_b in itertools.product(range(p), range(p)):
                cur_idx = t,sidx,pidx_a,pidx_b
                try:
                    valid_lattice = lattice[t,all_prev_indices[cur_idx[1:]]]
                    best_prev_idx = np.unravel_index(np.argmax(valid_lattice), valid_lattice.shape)
                    best_idx_score = lattice[best_prev_idx] + sflows[best_prev_idx[1]]
                except:
                    ipy.embed()
                lattice[cur_idx] = best_idx_score

        best_so_far = lattice[t,:,:,:].max()
        best_indices = [tuple(idx) for idx in np.argwhere(lattice[t,:,:,:]==best_so_far)]
        print(f"Minute {t}: best score = {best_so_far} at {len(best_indices)} paths")

    best_score = lattice[-1,:,:,:].max()
    best_idx = tuple(ax[0] for ax in np.where(lattice==best_score))
    print("")
    print("Best path:", paths[best_idx])
    print("Best score:", best_score)
    print("Practice score should be 1707")
    return best_score


def q1(filename):
    flows, edges, dists = read_input(filename)
    max_flow = dynamic_progress(flows, dists)
    print("Max flow:", max_flow)

def q2(filename):
    flows, edges, dists = read_input(filename)
    max_flow = dynamic_progress_pair(flows, edges, dists, time=26)
    print("Max flow:", max_flow)

if __name__=="__main__":
    # print("\n== Part 1 ==")
    # q1(sys.argv[1])
    print("\n== Part 2 ==")
    q2(sys.argv[1])
