from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical


class ActorCritic(nn.Module):
    def __init__(self, input_dim: int, action_dim: int, hidden_sizes: List[int]):
        super().__init__()
        layers: List[nn.Module] = []
        prev = input_dim
        for hidden in hidden_sizes:
            layers += [nn.Linear(prev, hidden), nn.ReLU()]
            prev = hidden
        self.body = nn.Sequential(*layers)
        self.actor = nn.Linear(prev, action_dim)
        self.critic = nn.Linear(prev, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.body(x)
        return self.actor(z), self.critic(z)


@dataclass
class RolloutBuffer:
    states: List[np.ndarray] = field(default_factory=list)
    actions: List[int] = field(default_factory=list)
    log_probs: List[float] = field(default_factory=list)
    rewards: List[float] = field(default_factory=list)
    dones: List[bool] = field(default_factory=list)
    values: List[float] = field(default_factory=list)

    def clear(self) -> None:
        self.states.clear()
        self.actions.clear()
        self.log_probs.clear()
        self.rewards.clear()
        self.dones.clear()
        self.values.clear()


class PPOTrainer:
    def __init__(
        self,
        input_dim: int,
        action_dim: int,
        hidden_sizes: List[int],
        actor_lr: float = 3e-4,
        critic_lr: float = 1e-3,
        clip_ratio: float = 0.2,
        gamma: float = 0.99,
        epochs: int = 4,
    ):
        self.gamma = gamma
        self.clip_ratio = clip_ratio
        self.epochs = epochs
        self.model = ActorCritic(input_dim, action_dim, hidden_sizes)
        self.actor_optim = optim.Adam(list(self.model.body.parameters()) + list(self.model.actor.parameters()), lr=actor_lr)
        self.critic_optim = optim.Adam(list(self.model.body.parameters()) + list(self.model.critic.parameters()), lr=critic_lr)

    def select_action(self, state: np.ndarray) -> Tuple[int, float, float]:
        state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        logits, value = self.model(state_t)
        dist = Categorical(logits=logits)
        action = dist.sample()
        return int(action.item()), float(dist.log_prob(action).item()), float(value.item())

    def _returns(self, rewards: List[float], dones: List[bool]) -> torch.Tensor:
        ret = []
        running = 0.0
        for reward, done in zip(reversed(rewards), reversed(dones)):
            if done:
                running = 0.0
            running = reward + self.gamma * running
            ret.append(running)
        ret.reverse()
        return torch.tensor(ret, dtype=torch.float32)

    def update(self, buffer: RolloutBuffer) -> Dict[str, float]:
        if not buffer.states:
            return {"actor_loss": 0.0, "critic_loss": 0.0}
        states = torch.tensor(np.asarray(buffer.states), dtype=torch.float32)
        actions = torch.tensor(buffer.actions, dtype=torch.long)
        old_log_probs = torch.tensor(buffer.log_probs, dtype=torch.float32)
        returns = self._returns(buffer.rewards, buffer.dones)
        old_values = torch.tensor(buffer.values, dtype=torch.float32)
        advantages = returns - old_values
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        actor_loss_val = 0.0
        critic_loss_val = 0.0
        for _ in range(self.epochs):
            logits, values = self.model(states)
            dist = Categorical(logits=logits)
            log_probs = dist.log_prob(actions)
            ratios = torch.exp(log_probs - old_log_probs)
            unclipped = ratios * advantages
            clipped = torch.clamp(ratios, 1 - self.clip_ratio, 1 + self.clip_ratio) * advantages
            actor_loss = -torch.min(unclipped, clipped).mean()
            critic_loss = ((returns - values.squeeze(-1)) ** 2).mean()

            self.actor_optim.zero_grad()
            actor_loss.backward(retain_graph=True)
            self.actor_optim.step()

            self.critic_optim.zero_grad()
            critic_loss.backward()
            self.critic_optim.step()

            actor_loss_val = float(actor_loss.item())
            critic_loss_val = float(critic_loss.item())

        buffer.clear()
        return {"actor_loss": actor_loss_val, "critic_loss": critic_loss_val}
