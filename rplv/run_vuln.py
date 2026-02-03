# main.py

# from vuln.awe import compute_per_node_samples, get_allowed_walks #, AWNode, AWTree, get_anonymous_walks,
#from vuln.walks import get_random_walk, anonymize, generate_anonymous_walks, compute_embedding, pll_init_node_embedding
from vuln.helpers import extract_subgraph, xy_from_graph, local_density_radius ,remove_isolates, remove_edges# precompute_neighbors,
from vuln.distances import dot, cosine_sim, kl_div, js_div, compute_distances
from vuln.AnonymousWalkKernel import AnonymousWalks
from common import generate_paxis, vec_to_pattern_dicts, s2m
import networkx as nx
import pandas as pd
import numpy as np
from funcy import join
from mpyll import parallelize
import time
# import os
import argparse


def run_experiments(experiments, attack_probability, graph, walk_length, N_EXP, init_node_embeddings, bias='none', densities=None, labels=None):
    expected_js = { node: 0 for node in graph.nodes() }
    expected_cos = { node: 0 for node in graph.nodes() }
    expected_euc = { node: 0 for node in graph.nodes() }
    for exp in experiments:
        # Generate the attacked graph (P) by removing edges with probability p.
        P = remove_edges(graph, attack_probability)
        aw_P = AnonymousWalks(P)
        node2vec_P, _ = aw_P.node_aw_embeddings(steps=walk_length-1, labels=labels, keep_last=True, bias=bias, densities=densities)
        node_repr_P = vec_to_pattern_dicts(node2vec_P, meta['meta-paths'], sparse=False)
        for node in P.nodes():
            # js, cos, euc = compute_distances(node_repr_P[node], init_node_embeddings[node])
            cos, euc = compute_distances(node_repr_P[node], init_node_embeddings[node])
            # Average the distances over the experiments.
            #expected_js[node] += js / N_EXP
            expected_cos[node] += cos / N_EXP
            #expected_euc[node] += euc / N_EXP
    #return [expected_js, expected_cos, expected_euc]
    return [expected_cos, expected_cos]




# i/o
parser = argparse.ArgumentParser()
parser.add_argument("--input-graph", "-i", dest="input_graph", required=True, help="Path to graphml file")
parser.add_argument("--output", "-o", dest="output_file", help="Path to output file. A csv file")
parser.add_argument("--walk-length", "-w", dest="walk_length", type=int, default=5, help="length of the random walks to sample.")
parser.add_argument("--epsilon", "-e", dest="epsilon", type=float, default=0.15, help="tuning parameter of anonymous walks sampling. see Eq.2, Anonymous Walk Embeddings (Ivanov and Burnaev 2018)")
parser.add_argument("--delta", "-d", dest="delta", type=float, default=0.1, help="tuning parameter of anonymous walks sampling.")
parser.add_argument("--n-exp", "-n", dest="n_exp", type=int, default=250, help="number of runs for each attack probability (computation of average risk)")
parser.add_argument("--bias", "-b", dest="bias", choices=['none', 'low_degree', 'high_degree', 'low_density', 'high_density'], default='none', help="bias of the random walks")
parser.add_argument("--radius", "-r", dest="radius", default=0, type=int, help="raidus")

args = parser.parse_args()
INPUT_GRAPH = args.input_graph
OUTPUT_FILE = args.output_file
EPS = args.epsilon
DELTA = args.delta
WALK_LENGTH = args.walk_length
N_EXPERIMENTS = args.n_exp
BIAS = args.bias
RADIUS = args.radius

# attack probabilities setup
PROB_STEP = 0.1
attack_probabilities = generate_paxis(PROB_STEP, [0.93, 0.96, 0.99])
# num_samples = compute_per_node_samples()

print('# INITIALIZATIONS')
print('  1. loading graph...')
G = nx.read_graphml(INPUT_GRAPH)
H = G.copy()
if BIAS in ['low_density', 'high_density']:
    if RADIUS == 'none':
        raise ValueError("null radius. can not compute density")
    nodes, XY = xy_from_graph(G)
    density_map = local_density_radius(H, RADIUS) # denstiy radius to be added in args
else:
    nodes= list(H.nodes())
    density_map=None
    radius=None
# bias

labels=None
print('  2. computing initial node embeddings...')
start = time.time()
aw_G = AnonymousWalks(H)
node2vec_G, meta = aw_G.node_aw_embeddings(steps=WALK_LENGTH-1, labels=labels, keep_last=True, bias=BIAS, densities=density_map)
end = time.time()
duration =  s2m(end - start)
print(f'   time elapsed: {duration[0]} mins and {duration[1]} seconds.')
init_node_embeddings = vec_to_pattern_dicts(node2vec_G, meta['meta-paths'], sparse=False)
print('  done.')



print('# CONSTRUCTING VULNERABILITY PROFILES')
start_time = time.time()
probability_to_impacts = {}
for p in attack_probabilities:
    p_start_time = time.time()
    # Initialize accumulators for distance metrics for every node.
    expected_js = {node: 0 for node in H.nodes()}
    expected_cos = {node: 0 for node in H.nodes()}
    expected_euc = {node: 0 for node in H.nodes()}
    if p == 0:
        probability_to_impacts[p] = {
        'js': expected_js,
        'cos': expected_cos,
        'euc': expected_euc}
    else:
        experiments = list(range(N_EXPERIMENTS))
        # Parallelize experiment
        results = parallelize(
                task = run_experiments,
                data = experiments,
                n_jobs = -1,
                run_experiments_attack_probability = p,
                run_experiments_graph = H,
                run_experiments_walk_length = WALK_LENGTH,
                run_experiments_N_EXP = N_EXPERIMENTS,
                run_experiments_init_node_embeddings = init_node_embeddings,
                run_experiments_bias = BIAS,
                run_experiments_densities = density_map,
                )
        for node in nodes: # list order here is important
            # maybe this is where the problems come from.
                #expected_js[node] = sum([res[0][node] for res in results])
                expected_cos[node] = sum([res[0][node] for res in results])
                expected_euc[node] = sum([res[1][node] for res in results])

        # Store the per-node averages for this attack probability.
        probability_to_impacts[p] = {
            #'js': expected_js,
            'cos': expected_cos,
            'euc': expected_euc
        }
        p_end_time = time.time()
        print(f'             Attack probability p ={p}: {int((p_end_time - p_start_time)/60)} minutes and {int((p_end_time - p_start_time) % 60)} seconds')
end_time = time.time()

print(f'elapsed time :{int((end_time - start_time) // 60)} minutes and {int((end_time - start_time) % 60)} seconds')
print('Parameters:')
print(f'    - WALK_LENGTH = {WALK_LENGTH}')
# print(f'    - NUM_SAMPLES = {num_samples}')
print(f'    - N_EXPERIMENTS = {N_EXPERIMENTS}')
print(f'    - N PROBABILITY = {len(attack_probabilities)}')



for p,_ in probability_to_impacts.items():
    #nx.set_node_attributes(H, probability_to_impacts[p]['js'], f'impact_js_{round(p, 2)}')
    nx.set_node_attributes(H, probability_to_impacts[p]['cos'], f'impact_cos_{round(p, 2)}')
    nx.set_node_attributes(H, probability_to_impacts[p]['euc'], f'impact_euc_{round(p, 2)}')


#nx.write_graphml(H,'output/graph_results.graphml')
df = pd.DataFrame.from_dict(dict(H.nodes(data=True)), orient='index').rename_axis('node_id')
df.index = df.index.astype(str)
df.to_csv(OUTPUT_FILE)
print('   FINISHED.')
