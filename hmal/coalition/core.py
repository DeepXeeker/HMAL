from __future__ import annotations

from itertools import chain, combinations
from typing import Dict, Iterable, List, Sequence, Tuple


def discounted_sum(values: Sequence[float], gamma: float) -> float:
    return sum((gamma ** t) * value for t, value in enumerate(values))


def coalition_value(env_rewards: Sequence[float], action_costs: Sequence[float], gamma: float) -> float:
    return discounted_sum(env_rewards, gamma) - discounted_sum(action_costs, gamma)


def powerset(items: Sequence[str]) -> Iterable[Tuple[str, ...]]:
    return chain.from_iterable(combinations(items, r) for r in range(1, len(items) + 1))


def evaluate_core_feasibility(
    grand_coalition: Sequence[str],
    coalition_worth: Dict[Tuple[str, ...], float],
    allocations: Dict[str, float],
) -> Dict[str, float]:
    violations = []
    for subset in powerset(tuple(sorted(grand_coalition))):
        worth = coalition_worth.get(tuple(sorted(subset)), 0.0)
        alloc = sum(allocations.get(player, 0.0) for player in subset)
        violations.append(max(0.0, worth - alloc))
    max_margin = max(violations) if violations else 0.0
    violation_rate = float(sum(v > 0 for v in violations)) / max(1, len(violations))
    return {"violation_margin": max_margin, "violation_rate": violation_rate}
