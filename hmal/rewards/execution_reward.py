from __future__ import annotations

from typing import Dict


def compute_execution_reward(
    mission_gain: float,
    risk_reduction: float,
    action_name: str,
    action_costs: Dict[str, float],
    projected_disruption: float = 0.0,
    invalid_action_penalty: float = 0.0,
) -> float:
    cost = abs(action_costs.get(action_name, 0.0))
    reward = mission_gain + risk_reduction - cost - projected_disruption - invalid_action_penalty
    return float(reward)
