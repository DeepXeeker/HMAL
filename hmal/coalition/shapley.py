from __future__ import annotations

import random
from typing import Dict, Iterable, List, Sequence, Tuple


CoalitionWorth = Dict[Tuple[str, ...], float]


def approximate_shapley(players: Sequence[str], worth: CoalitionWorth, num_permutations: int = 200) -> Dict[str, float]:
    players = list(players)
    contrib = {p: 0.0 for p in players}
    for _ in range(num_permutations):
        perm = players[:]
        random.shuffle(perm)
        prefix: List[str] = []
        prev_value = 0.0
        for player in perm:
            prefix.append(player)
            coalition = tuple(sorted(prefix))
            current_value = worth.get(coalition, 0.0)
            contrib[player] += current_value - prev_value
            prev_value = current_value
    return {p: v / max(1, num_permutations) for p, v in contrib.items()}
