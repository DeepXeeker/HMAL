from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

import numpy as np


@dataclass
class TabularQSelector:
    modes: List[str]
    alpha: float = 0.1
    gamma: float = 0.99
    epsilon: float = 0.1
    q_table: Dict[str, np.ndarray] = field(default_factory=dict)

    def _ensure(self, state_key: str) -> np.ndarray:
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(len(self.modes), dtype=np.float32)
        return self.q_table[state_key]

    def act(self, state_key: str, explore: bool = True) -> str:
        q = self._ensure(state_key)
        if explore and np.random.rand() < self.epsilon:
            return str(np.random.choice(self.modes))
        return self.modes[int(np.argmax(q))]

    def update(self, state_key: str, mode: str, reward: float, next_state_key: str) -> None:
        q = self._ensure(state_key)
        next_q = self._ensure(next_state_key)
        action_idx = self.modes.index(mode)
        target = reward + self.gamma * float(np.max(next_q))
        q[action_idx] = q[action_idx] + self.alpha * (target - q[action_idx])
