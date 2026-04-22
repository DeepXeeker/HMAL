from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict

import numpy as np

from hmal.models.tier1_q import TabularQSelector


@dataclass
class Tier1Selector:
    learner: TabularQSelector

    @staticmethod
    def state_key(summary: Dict[str, float]) -> str:
        rounded = {k: round(float(v), 3) for k, v in sorted(summary.items())}
        return json.dumps(rounded, sort_keys=True)

    def select_mode(self, summary: Dict[str, float], explore: bool = True) -> str:
        return self.learner.act(self.state_key(summary), explore=explore)

    def update(self, summary: Dict[str, float], mode: str, reward: float, next_summary: Dict[str, float]) -> None:
        self.learner.update(self.state_key(summary), mode, reward, self.state_key(next_summary))
