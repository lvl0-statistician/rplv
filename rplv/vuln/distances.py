# distances.py

import numpy as np

def dot(u, v):
    dot = [u*v for u,v in zip(u,v)]
    return sum(dot)

def cosine_sim(u,v):
    dot_uv = dot(u,v)
    norm_u = dot(u,u)**(0.5)
    norm_v = dot(v,v)**(0.5)
    if norm_u == 0 or norm_v == 0:
        return 0
    else:
        return dot_uv/(norm_u*norm_v)

def kl_div(P, Q):
    P = { k: v for k, v in P.items() }
    Q = { k: v for k, v in Q.items() }
    support = list(P.keys())
    kl = [ P[x] * np.log(P[x]/Q[x]) for x in support if P[x]!=0 ]
    return sum(kl)

def js_div(P, Q):
    support = list(P.keys())
    M = { x: (P[x]+Q[x])/2 for x in support }
    div_PM = kl_div(P, M)
    div_QM = kl_div(Q, M)
    return 0.5*div_PM + 0.5*div_QM

def compute_distances(disturbed, init):
    walk_length = len(list(init.keys())[0])
    sorted_aws = sorted(init.keys())
    disturbed = {k: v for k,v in disturbed.items() if k != (0,)*walk_length}
    init = {k: v for k,v in init.items() if k != (0,)*walk_length}
    # js = np.sqrt(js_div(disturbed, init))
    init_embedding = [init[aw] for aw in sorted_aws]
    disturbed_embedding = [disturbed[aw] for aw in sorted_aws]
    cosine_dist = 1 - cosine_sim(disturbed_embedding, init_embedding)
    euclidean = np.linalg.norm(np.array(disturbed_embedding) - np.array(init_embedding))
    #return js, cosine_dist, euclidean
    return cosine_dist, euclidean
