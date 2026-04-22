from __future__ import annotations

import hashlib
from typing import Iterable, List

import numpy as np


def bounded_hash(value: str, modulo: int = 128) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest, 16) % modulo


def bucketize(value: float, bins: Iterable[float]) -> int:
    edges = list(bins)
    for idx, edge in enumerate(edges):
        if value <= edge:
            return idx
    return len(edges)


def hashed_one_hot(tokens: Iterable[str], dim: int = 128) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    for token in tokens:
        vec[bounded_hash(str(token), dim)] += 1.0
    return vec
