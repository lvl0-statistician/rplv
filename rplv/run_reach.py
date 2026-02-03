# run_reach.py

import networkx as nx
import pandas as pd
import numpy as np
import time
from reach.attacks import simulate_attack, recalculated_degree_attack, recalculated_betweenness_attack, monte_carlo_random_attack
from reach.helpers import grep_column_names, extract_metric_dataframe, sort
from reach.reachability import compute_reachability_index, evaluate_params, search_params
from common import generate_paxis, compute_auc, s2m
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input-graph", "-i", dest="input_graph", required=True, help="Path to graphml file")
parser.add_argument("--input-data", "-d", dest="input_data", required=True, help="impact dataframe from 'run_vuln.py'")
parser.add_argument("--metric", "-m", dest="metric", choices=['cos','euc', 'js'], default="cos", help="distance function for embeddings")
parser.add_argument("--output-lcc", "-l", dest="output_lcc", required=True, help="path to results of attack strategies. a csv.")
parser.add_argument("--output-scores", "-s", dest="output_scores", required=True, help="path to robustness scores of attack strategies. a csv.")
parser.add_argument("--output-params", "-r", dest="output_params", required=True, help="path to reachability index parameters. a csv.")

args = parser.parse_args()
INPUT_GRAPH = args.input_graph
INPUT_DATA = args.input_data
OUTPUT_LCC = args.output_lcc
OUTPUT_SCORES = args.output_scores
OUTPUT_PARAMS = args.output_params
METRIC = args.metric

PROB_STEP = 0.1 # argparse input
EXTENSION = [0.93, 0.96, 0.99]

print('# REACHABILITY')
G = nx.read_graphml(INPUT_GRAPH)
G_copy = nx.Graph(G) # force simple graph
df = pd.read_csv(INPUT_DATA) # output from vuln.py
df = df.set_index("node_id")
df.index = df.index.astype(str)
df_metric = extract_metric_dataframe(df, METRIC, G_copy)

print('   Computing expected risk...')
attack_probability = generate_paxis(PROB_STEP, EXTENSION)
df_metric.loc[:, 'expected_risk'] = df_metric.apply(lambda row: np.trapz(row.values[1::], attack_probability), axis=1)

print('   Tuning reachability index...')
discount_factors = [round(e, 2) for e in np.linspace(0, 1, 100, endpoint = False)]
max_distances = np.linspace(1, 10, 10, dtype = int)
expected_risk = df_metric['expected_risk'].to_dict()

start = time.time()
best_params, best_auc, results = search_params(G_copy,
                                                   expected_risk,
                                                   discount_factors,
                                                   max_distances[1::]
                                                   )
end = time.time()
best_df, best_md = best_params # best discount facto and max dist. L
reachability_best = {node: compute_reachability_index(node, G_copy, expected_risk, best_df, best_md) for node in G_copy.nodes}
mins, secs = s2m(end - start)
# print(f'      elapsed time {mins} minutes and {secs} seconds')

# orderings
expected_risk_ordr = sort(G_copy, expected_risk, descending=False)
reachability_ordr = sort(G_copy, reachability_best)
degree_ordr = sort(G_copy, G_copy.degree)
btw_ordr = sort(G_copy, nx.betweenness_centrality(G_copy))

# attacks
expected_risk_atk = simulate_attack(G_copy, expected_risk_ordr)
reachability_atk = simulate_attack(G_copy, reachability_ordr)
degree_atk = simulate_attack(G_copy, degree_ordr)
btw_atk = simulate_attack(G_copy, btw_ordr)

# store results

#params = pd.DataFrame({'discount_factor':best_params[0],
#                       'max_distance': best_params[1],
#                       'reachability_R': reachability_atk['robustness']})
relative_sizes = pd.DataFrame({'fraction': expected_risk_atk['fraction'],
                               'expected_risk_LCC': expected_risk_atk['relative_sizes'],
                               'reachability_LCC': reachability_atk['relative_sizes'],
                               'degree_LCC': degree_atk['relative_sizes'],
                               'btw_LCC': btw_atk['relative_sizes']
                               })

robustness = pd.DataFrame({'expected_risk_R': expected_risk_atk['robustness'],
                           'reachability_R': reachability_atk['robustness'],
                           'degree_R': degree_atk['robustness'],
                           'btw_R': btw_atk['robustness'],
                           }, index=['robustness'])

relative_sizes.to_csv(OUTPUT_LCC)
robustness.to_csv(OUTPUT_SCORES)
# params.to_csv(OUTPUT_PARAMS)
print('   FINISHED.')
