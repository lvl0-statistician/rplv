# reachability.py

import networkx as nx
import numpy as np
import multiprocessing
import warnings
from reach.attacks import simulate_attack
from common import compute_auc
warnings.filterwarnings('ignore')


def compute_reachability_index(node, graph, expected_risks, discount_factor, max_distance):
    """
    Compute reachability index of a node based on its L_neighborhood
    """
    L_neighborhood = nx.single_source_shortest_path_length(graph, source=node, cutoff=max_distance)
    N = graph.number_of_nodes()
    N_hop = len(L_neighborhood)
    reachability = 0
    for neighbor, distance in L_neighborhood.items():
        reachability = reachability + (discount_factor**distance)*expected_risks[neighbor]
    # return N_hop/N * reachability
    return reachability

def evaluate_params(args):
    """Evaluate a single grid search cell."""
    G, expected_risks, df, md = args
    # 1. Compute reachability for each node
    reachability = {node: compute_reachability_index(node, G, expected_risks, df, md) for node in G.nodes()}
    # 2. Order nodes by decreasing reachability
    ordering = sorted(G.nodes(), key=lambda n: reachability[n], reverse=True)
    # 3. Simulate attack using ordering
    relative_sizes = simulate_attack(G, ordering)
    # 4. Compute AUC from the resulting sizes
    auc = compute_auc(relative_sizes['relative_sizes'])
    return (df, md, auc)

def search_params(G, expected_risks, discount_factors, max_distances):
    # Prepare a list of all parameter combinations
    tasks = [(G, expected_risks, df, md) for df in discount_factors for md in max_distances]
    # Create a multiprocessing pool
    with multiprocessing.Pool() as pool:
        results_list = pool.map(evaluate_params, tasks)

    results = {}
    best_auc = float('inf')
    best_params = None
    for df, md, auc in results_list:
        results[(df, md)] = auc
        if auc < best_auc:
            best_auc = auc
            best_params = (df, md)

    return best_params, best_auc, results
