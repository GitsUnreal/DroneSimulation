
import numpy as np
from typing import Any

def normalize(vec: Any) -> Any:
    """
    Normalize a vector.
    Args:
        vec (Any): Vector to normalize.
    Returns:
        Any: Normalized vector.
    """
    norm = np.linalg.norm(vec)
    if norm > 0:
        return vec / norm
    return np.zeros_like(vec)

def distance(a: Any, b: Any) -> float:
    """
    Calculate Euclidean distance between two vectors.
    Args:
        a (Any): First vector.
        b (Any): Second vector.
    Returns:
        float: Distance.
    """
    return float(np.linalg.norm(a - b))
