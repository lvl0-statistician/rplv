# attacks.py

import networkx as nx
import numpy as np
import random
from common import compute_auc


def simulate_attack(G, ordering):
    """
    Simulate an attack on graph G by removing nodes in the given ordering.
    Parameters:
      - Graph
      - Ordered nodes
    Returns:
      - Dictionnary of:
            * 'relative_sizes': list of relative sizes of LCC after each node removal.
            * 'fraction': list of cumulative fraction of removed nodes after each removal.
            * 'robustness': Robustness metric for the attack.
    """
    attack_results = {}
    H = G.copy()
    # get initial lcc size
    initial_lcc = len(max(nx.connected_components(H), key=len))
    relative_sizes = [1.0]  # first relative size = 1
    for node in ordering:
        if node in H:
            H.remove_node(node)
        if len(H) > 0:
            current_lcc = len(max(nx.connected_components(H), key=len))
            relative_sizes.append(current_lcc / initial_lcc)
        else:
            relative_sizes.append(0)


    fraction = [i/len(ordering) for i in range(len(relative_sizes))]
    attack_results.update(
            {
                'relative_sizes': relative_sizes,
                'fraction': fraction,
                'robustness': compute_auc(relative_sizes)
                }
            )

    return attack_results

def monte_carlo_random_attack(G: nx.Graph,
                              num_simulations: int = 100,
                              seed = None):
    """
    Performs Monte Carlo simulation of random attacks on a graph by removing nodes
    one by one until the graph is empty, and measuring the relative size of the
    largest connected component after each node removal.

    Parameters:
    -----------
    G : networkx.Graph
    num_simulations : Number of Monte Carlo simulations to perform
    seed : (optional) Random seed for reproducibility

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray]
        Two arrays containing:
        1. The average relative size of the largest connected component after each node removal
        2. The standard deviation of those relative sizes across all simulations
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    num_nodes = G.number_of_nodes()
    if num_nodes == 0:
        return np.array([0.0]), np.array([0.0])

    # Array to store results from all simulations
    # +1 because we include the initial state before any removal
    all_results = np.zeros((num_simulations, num_nodes + 1))

    for sim in range(num_simulations):
        G_copy = G.copy()
        # Initial size of the largest connected component
        components = list(nx.connected_components(G_copy))
        if components:
            initial_size = len(max(components, key=len))
        else:
            # Handle the case where there are no connected components
            initial_size = 0
        # If initial_size is 0, all relative sizes will be 0/0, set to 0
        if initial_size == 0:
            all_results[sim, :] = 0.0
            continue
        # Set the initial state (no nodes removed yet)
        all_results[sim, 0] = 1.0
        # List of nodes that can be removed
        removable_nodes = list(G_copy.nodes())
        for step in range(num_nodes):
            # Break if there are no more nodes to remove
            if not removable_nodes:
                break
            # Randomly remove a node to remove
            node_to_remove = random.choice(removable_nodes)
            G_copy.remove_node(node_to_remove)
            removable_nodes.remove(node_to_remove)
            # Calculate the size of the largest connected component
            if G_copy.number_of_nodes() > 0:
                components = list(nx.connected_components(G_copy))
                if components:
                    largest_cc_size = len(max(components, key=len))
                    relative_size = largest_cc_size / initial_size
                else:
                    relative_size = 0.0
            else:
                relative_size = 0.0
            all_results[sim, step+1] = relative_size
    # Calculate the mean and standard deviation across all simulations for each step
    mean_results = np.mean(all_results, axis=0)
    std_results = np.std(all_results, axis=0)

    return mean_results, std_results

def recalculated_betweenness_attack(G):
    G_copy = G.copy()
    relative_sizes = [1]
    original_size = len(G.nodes)
    while len(G_copy.nodes) > 0:
        betweenness = nx.betweenness_centrality(G_copy)
        # Find the node with the highest betweenness centrality
        node_to_remove = max(betweenness, key=betweenness.get)
        G_copy.remove_node(node_to_remove)
        # After removal, calculate the largest connected component
        if len(G_copy) == 0:
            relative_sizes.append(0)
        else:
            largest_cc = max(nx.connected_components(G_copy), key=len)
            largest_cc_size = len(largest_cc) / original_size
            relative_sizes.append(largest_cc_size)

    return relative_sizes

def recalculated_degree_attack(G):
    G_copy = G.copy()
    relative_sizes = [1]
    original_size = len(G_copy.nodes)
    while len(G_copy.nodes) > 0:
        degree = dict(nx.degree(G_copy))
        node_to_remove = max(degree, key=degree.get)
        G_copy.remove_node(node_to_remove)
        # After removal, calculate the largest connected component
        if len(G_copy) == 0:
            relative_sizes.append(0)
        else:
            largest_cc = max(nx.connected_components(G_copy), key=len)
            largest_cc_size = len(largest_cc) / original_size
            relative_sizes.append(largest_cc_size)

    return relative_sizes
