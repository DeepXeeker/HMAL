from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

from hmal.models.ppo import PPOTrainer, RolloutBuffer


@dataclass
class Tier2PolicyBank:
    input_dim: int
    hidden_sizes: List[int]
    action_spaces: Dict[str, List[str]]
    actor_lr: float = 3e-4
    critic_lr: float = 1e-3
    clip_ratio: float = 0.2
    gamma: float = 0.99
    epochs: int = 4
    trainers: Dict[str, PPOTrainer] = field(init=False)
    buffers: Dict[str, RolloutBuffer] = field(init=False)

    def __post_init__(self) -> None:
        self.trainers = {
            mode: PPOTrainer(
                input_dim=self.input_dim,
                action_dim=len(actions),
                hidden_sizes=self.hidden_sizes,
                actor_lr=self.actor_lr,
                critic_lr=self.critic_lr,
                clip_ratio=self.clip_ratio,
                gamma=self.gamma,
                epochs=self.epochs,
            )
            for mode, actions in self.action_spaces.items()
        }
        self.buffers = {mode: RolloutBuffer() for mode in self.action_spaces}

    def select(self, mode: str, state: np.ndarray) -> Tuple[str, int, float, float]:
        trainer = self.trainers[mode]
        action_idx, log_prob, value = trainer.select_action(state)
        action_name = self.action_spaces[mode][action_idx]
        return action_name, action_idx, log_prob, value

    def store(self, mode: str, state: np.ndarray, action_idx: int, log_prob: float, reward: float, done: bool, value: float) -> None:
        buf = self.buffers[mode]
        buf.states.append(state)
        buf.actions.append(action_idx)
        buf.log_probs.append(log_prob)
        buf.rewards.append(reward)
        buf.dones.append(done)
        buf.values.append(value)

    def update(self, mode: str) -> Dict[str, float]:
        return self.trainers[mode].update(self.buffers[mode])
