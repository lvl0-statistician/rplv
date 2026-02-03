# utils.py

import numpy as np

def generate_paxis(PROB_STEP, extension=None):
    """
    Generates the attack probability axis with equally spaced increments.
    The axis can be extended by appending new points (e.g [0.93, 0.95, 0.99]).
    """
    axis = np.linspace(0, 1, num=int(1/PROB_STEP), endpoint=False)
    axis = [round(p, 2) for p in axis]
    if extension:
        return axis + extension
    else:
        return axis

def compute_auc(relative_sizes):
    """
    Compute AUC of the LCC size vs fraction of removed nodes
    """
    N = len(relative_sizes) - 1  # no of removal steps (removing size 1)
    dx = 1/N if N > 0 else 1
    auc = np.trapz(relative_sizes, dx=dx)
    return auc


def s2m(duration): # to be moved to helpers
    mins = int(duration/60)
    seconds = int(duration % 60)
    return (mins, seconds)

def vec_to_pattern_dicts(node2vec, patterns, sparse=False):
    out = {}
    for n, vec in node2vec.items():
        if sparse:
            out[n] = {tuple(p): v for p, v in zip(patterns, vec) if v != 0.0}
        else:
            out[n] = {tuple(p): v for p, v in zip(patterns, vec)}
    return out
