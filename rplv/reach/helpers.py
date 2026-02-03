# helpers.py

import pandas as pd
import numpy as np

def sort(graph, dictionary, descending=True):
    return sorted(graph.nodes, key=lambda n: dictionary[n], reverse=descending)

def grep_column_names(df, inclusions_list):
    grepped = [col for col in df.columns if any(inclusion in col for inclusion in inclusions_list)]

    return(grepped)

def extract_metric_dataframe(df, metric_choice, graph):
    df_copy = df.copy()

    df_copy['degree'] = df.index.map(dict(graph.degree))
    if isinstance(metric_choice, str) and metric_choice in ['cos','euc', 'js']:
        metric_columns = sorted(grep_column_names(df_copy, [f'impact_{metric_choice}', 'degree']))
        return df_copy[metric_columns]
    # elif isinstance(metric_choice, list) and len(metric_choice) == 3:
    #     metrics_cols = {metric: sorted(grep_column_names(df_copy, [f'impact_{metric}', 'degree'])) for metric in metric_choice}
    #     df1, df2, df3 = [df_copy[metrics_cols.get(metric)] for metric in metrics_cols.keys()]
    #     return df1, df2, df3
    else:
        raise ValueError("positional argument 'metric_choice' must be either one of 'cos', 'js', 'euc' or a list of exactly these three.")
