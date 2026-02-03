# awe.py

import numpy as np

class AWNode(object):

    def __init__(self, data, maxi):
        self.data = data
        self.maxi = maxi
        self.parent = None
        self.children = list()

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def add_children(self, children):
        for child in children:
            self.add_child(child)

class AWTree(object):

    def __init__(self):
        self.root = AWNode(data = 1, maxi = 1)

def get_anonymous_walks(walk_length):
    if not isinstance(walk_length, int) or walk_length < 1:
        raise ValueError('Invalid walk length')
    # develop tree
    tree = AWTree()
    leafs = [tree.root]
    tree_level = 1
    while tree_level < walk_length:
        leafs_new = list()
        for leaf in leafs:
            children = [
                AWNode(data = i, maxi = i if i > leaf.maxi else leaf.maxi)
                for i in range(1, leaf.maxi + 2)
            ]
            leaf.add_children(children)
            leafs_new += children
        leafs = leafs_new
        tree_level += 1
    # get walks
    walks = list()
    for leaf in leafs:
        walk = list()
        n = leaf
        while n.parent != None:
            walk.insert(0, n.data)
            n = n.parent
        walk.insert(0, 1)
        walks.append(tuple(walk))
    return walks

def compute_per_node_samples(length, epsilon=0.1, delta=0.01):
    """
    Eq. 2 in Anonymous Walk Embeddings, Sergey Ivanov
    """
    etas = {2: 2, 3: 5, 4: 15, 5: 52, 6: 203, 7: 877, 8: 4140}
    eta = etas[length]
    x = np.ceil((2 / (epsilon ** 2)) * (np.log(float(2**int(eta) - 2)) - np.log(delta)))
    return int(x)

def get_allowed_walks(all_walks):
    """
    Removes self loops from anonymous walks
    """
    to_remove = []
    for aw in all_walks:
        i = 0
        current = aw[i]
        while i < len(aw)-1:
            after = aw[i+1]
            if current != after:
                current = after
                i = i+1
            else:
                to_remove.append(aw)
                # terminate while loop
                i = len(aw) + 1
    allowed_walks = all_walks
    for w in to_remove:
        allowed_walks.remove(w)
    return allowed_walks
