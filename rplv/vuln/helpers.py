# helpers.py

import networkx as nx
import numpy as np
from scipy.spatial import cKDTree as KDTree
def remove_isolates(graph):
    isolated_nodes = list(nx.isolates(graph))
    graph.remove_nodes_from(isolated_nodes)

def remove_edges(graph, probability):
    disturbed_graph = graph.copy()
    for edge in list(disturbed_graph.edges()):
        bernoulli_outcome = np.random.binomial(1, probability)
        if bernoulli_outcome == 1 :
            disturbed_graph.remove_edge(*edge)

    return disturbed_graph

def precompute_neighbors(graph):
    """
    Precompute a dictionary mapping each node to its list of neighbors.
    """
    neighbor_dict = {node: list(graph.neighbors(node)) for node in graph.nodes()}

    return neighbor_dict

def extract_subgraph(G, v, l):
    """
    Extracts a subgraph of length `l` around node `v` in graph `G`.

    Parameters:
    - G: NetworkX graph
    - v: The center node (around which to extract the subgraph)
    - l: The maximum length (number of hops)

    Returns:
    - subgraph: NetworkX subgraph containing nodes and edges within `l` hops from `v`
    """

    # get all nodes within `l` hops from node `v`
    nodes_within_l_hops = nx.single_source_shortest_path_length(G, v, cutoff=l)

    # extract the subgraph using the nodes found
    subgraph_nodes = list(nodes_within_l_hops.keys())
    subgraph = G.subgraph(subgraph_nodes).copy()

    return subgraph

def get_nth_component(graph, n):
    lcc = sorted(nx.connected_components(graph), key=len, reverse=True)[n]
    induced = graph.subgraph(lcc)
    return induced

def xy_from_graph(G: nx.Graph):
    """Return node_id list and N×2 array of [x,y]."""
    nodes = []
    coords = []
    for n, d in G.nodes(data=True):
        if "x" not in d or "y" not in d:
            raise ValueError(f"Node {n} is missing 'x' or 'y' attributes.")
        nodes.append(n)
        coords.append([float(d["x"]), float(d["y"])])
    XY = np.asarray(coords)
    return nodes, XY


def local_density_radius(G, r, exclude_self=False, write_back=False, attr_name=None):
    """
    r: radius in the same units as x,y (e.g., meters).
    Returns dict {node: density_i}, where density_i = k_i / (pi r^2).
    If write_back=True, stores under node attribute `attr_name` (default: f"density_r{r}").
    """
    if r <= 0:
        raise ValueError("r must be positive.")
    nodes, XY = xy_from_graph(G)

    # fast neighbor counting
    tree = KDTree(XY)
    # query all points at once
    # SciPy cKDTree: query_ball_point can take an array of points

    neighborhoods = tree.query_ball_point(XY, r)
    counts = np.fromiter((len(idx) for idx in neighborhoods), dtype=int)
    #area = np.pi * (r ** 2)
    #densities = counts / area

    result = {n: float(v) for n, v in zip(nodes, counts)}
    if write_back:
        if attr_name is None:
            attr_name = f"density_r{r}"
        nx.set_node_attributes(G, result, name=attr_name)
    return result
