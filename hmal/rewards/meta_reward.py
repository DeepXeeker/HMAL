from __future__ import annotations

from typing import Dict, Iterable, Sequence


def evidence_guidance_bonus(mode: str, observation: Dict[str, float]) -> float:
    suspicious = float(observation.get("suspicious_score", 0.0))
    confirmed = float(observation.get("confirmed_score", 0.0))
    disruption = float(observation.get("service_disruption", 0.0))

    if mode == "Sense":
        return 1.0 * suspicious * (1.0 - confirmed)
    if mode == "Deceive":
        return 0.75 * suspicious * (1.0 - confirmed)
    if mode == "Recover":
        return 1.0 * confirmed + 0.5 * disruption
    if mode == "Idle":
        return max(0.0, 1.0 - suspicious - confirmed)
    return 0.0


def discounted_option_return(rewards: Sequence[float], gamma: float) -> float:
    return sum((gamma ** t) * r for t, r in enumerate(rewards))


def compute_meta_reward(
    mode: str,
    rewards: Sequence[float],
    observation_summary: Dict[str, float],
    gamma: float,
    guidance_weight: float = 0.1,
    immediate_only: bool = False,
    discount_option_credit: bool = True,
) -> float:
    if not rewards:
        env_term = 0.0
    elif immediate_only:
        env_term = float(rewards[0])
    elif discount_option_credit:
        env_term = discounted_option_return(rewards, gamma)
    else:
        env_term = sum(rewards) / len(rewards)
    bonus = guidance_weight * evidence_guidance_bonus(mode, observation_summary)
    return env_term + bonus
