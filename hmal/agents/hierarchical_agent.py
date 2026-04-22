from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from hmal.types import ActionProposal
from hmal.agents.tier1_selector import Tier1Selector
from hmal.agents.tier2_executor import Tier2PolicyBank


@dataclass
class HierarchicalAgent:
    selector: Tier1Selector
    executors: Tier2PolicyBank
    mode_to_actions: Dict[str, List[str]]

    def act(self, state_vector: np.ndarray, state_summary: Dict[str, float], explore: bool = True) -> ActionProposal:
        mode = self.selector.select_mode(state_summary, explore=explore)
        action_name, _, _, _ = self.executors.select(mode, state_vector)
        return ActionProposal(mode=mode, action_name=action_name, parameters={})
