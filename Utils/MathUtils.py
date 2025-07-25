import numpy as np

def normalize(vec):
    norm = np.linalg.norm(vec)
    if norm > 0:
        return vec / norm
    return np.zeros_like(vec)

def distance(a, b):
    return np.linalg.norm(a - b)
