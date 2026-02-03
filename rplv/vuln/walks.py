# walks.py

import random
from collections import Counter
from vuln.helpers import xy_from_graph, local_density_radius


def get_random_walk(start_node, walk_length, neighbor_dict, graph, bias='none', densities=None):
    """
    Sample a random walk of a given length starting from a given node.

    Parameters:
      start_node   : the starting node for the walk
      walk_length  : the total number of nodes in the walk
      neighbor_dict: a dict mapping node -> list of neighbors (precomputed)
      bias         : random walk bias. supported values are
                      - 'low_degree': bias walks towards low degree nodes
                      - 'high_degree' bias walks towards high degree nodes
                      - 'low_density' bias walks towards low density nodes
                      - 'high_density' bias walks towards high density nodes

    Returns:
      A list representing the random walk.
    """
    walk = [start_node]
    current = start_node
    for _ in range(1, walk_length):
        neighbors = neighbor_dict.get(current, [])
        if not neighbors:
            return [start_node] * walk_length
        if bias == 'none':
            next_node = random.choice(neighbors)
        elif bias == 'low_degree':
            degrees = [len(neighbor_dict[n]) for n in neighbors]
            weights = [1/d for d in degrees]
            weights = [w/sum(weights) for w in weights]
            next_node = random.choices(neighbors, weights=weights, k=1)[0]
        elif bias == 'high_degree':
            degrees = [len(neighbor_dict[n]) for n in neighbors]
            weights = degrees
            weights = [w/sum(weights) for w in weights]
            next_node = random.choices(neighbors, weights=weights, k=1)[0]
        elif bias == 'low_density':
            dsty = [densities[n] for n in neighbors]
            weights = [1/density for density in dsty]
            weights = [w/sum(weights) for w in weights]
            next_node = random.choices(neighbors, weights=weights, k=1)[0]
        elif bias == 'high_density':
            dsty = [densities[n] for n in neighbors]
            weights = [density for density in dsty]
            weights = [w/sum(weights) for w in weights]
            next_node = random.choices(neighbors, weights=weights, k=1)[0]

        walk.append(next_node)
        current = next_node
    return walk

def anonymize(random_walk):
    """
    Anonymize a random walk.
    Parameters:
      - random_walk: sequence of nodes corresponding to the walk. list
    Returns:
      - anonymous_walk: anonymized version of the walk.
    """
    anonymous_walk = [1]
    i = 1
    seen_nodes = {random_walk[0]: i}
    for node in random_walk[1:]:
        if node in seen_nodes.keys():
            anonymous_walk.append(seen_nodes[node])
        else:
            i += 1
            seen_nodes[node] = i
            anonymous_walk.append(seen_nodes[node])
    return anonymous_walk

def generate_anonymous_walks(node, walk_length, num_samples, neighbor_dict, graph, bias='none', densities=None):
    """
    Generator yielding anonymized random walks for a given node.
    Assumes the existence of a function `anonymize()` that maps a walk to its anonymous form, and a function `get_random_walk()`that generates a random walk from a graph for a given node.
    """
    for _ in range(num_samples):
        walk = get_random_walk(node, walk_length, neighbor_dict, graph,
                               bias, densities)
        anon_walk = anonymize(walk)
        yield tuple(anon_walk)

def compute_embedding(node, walk_length, num_samples, neighbor_dict, all_possible_anonymous_walks, graph, bias='none', densities=None):
    """
    For a given node, generates anonymous walks using a generator, accumulates their frequencies, then computes an embedding from the frequency distribution.

    Parameters:
      node                         : The current node.
      walk_length                  : The length of the random walks.
      num_samples                  : Number of walks to sample for the node.
      neighbor_dict                : Neighbors for the current (attacked) graph.
      all_possible_anonymous_walks : The complete set (or reference) of anonymous walks.
      bias                         : random walk bias (see get_random_walk())

    Returns:
      Dict of {aw : freq(aw)} pairs for the node.
    """
    node_embedding = Counter({aw: 0 for aw in all_possible_anonymous_walks})
    for anon_walk in generate_anonymous_walks(node, walk_length, num_samples, neighbor_dict, graph, bias, densities):
        node_embedding[anon_walk] += 1/num_samples
    return dict(node_embedding)


def pll_init_node_embedding(nodes, walk_length, num_samples, neighbor_dict, all_possible_anonymous_walks, graph, bias='none', densities=None):
    init_node_embedding = {}
    for node in nodes:
        init_node_embedding[node] = compute_embedding(
            node, walk_length, num_samples,
            neighbor_dict, all_possible_anonymous_walks, graph, bias, densities
        )
    return(init_node_embedding)
