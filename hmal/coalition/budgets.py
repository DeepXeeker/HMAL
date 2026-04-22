from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from hmal.types import ActionProposal


@dataclass
class BudgetState:
    max_zone_blocks_per_step: int = 1
    decoy_budget_fraction: float = 0.15
    episode_horizon: int = 500
    decoys_used: int = 0
    zone_blocks_this_step: int = 0

    @property
    def max_decoys(self) -> int:
        return int(self.episode_horizon * self.decoy_budget_fraction)

    def reset_step(self) -> None:
        self.zone_blocks_this_step = 0

    def can_execute(self, action: ActionProposal) -> bool:
        if action.action_name == "DeployDecoy" and self.decoys_used >= self.max_decoys:
            return False
        if action.action_name == "BlockTrafficZone" and self.zone_blocks_this_step >= self.max_zone_blocks_per_step:
            return False
        return True

    def register(self, action: ActionProposal) -> None:
        if action.action_name == "DeployDecoy":
            self.decoys_used += 1
        if action.action_name == "BlockTrafficZone":
            self.zone_blocks_this_step += 1
