from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from hmal.envs.base import BaseCyberEnv
from hmal.types import ActionProposal, StepResult


@dataclass
class CybORGCC4Env(BaseCyberEnv):
    mode_to_actions: Dict[str, List[str]]
    episode_horizon: int = 500
    _cyborg: Any = field(init=False, default=None)
    _step: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        try:
            from CybORG import CybORG  # type: ignore  # noqa: F401
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "CybORG is not installed. Install the official CybORG/CC4 package separately to use the simulation wrapper."
            ) from exc

    def reset(self) -> Dict[str, Any]:
        self._step = 0
        return {"events": [], "simulator": "cc4"}

    def step(self, action: ActionProposal) -> StepResult:
        self._step += 1
        terminated = self._step >= self.episode_horizon
        # This wrapper is intentionally light because actual CC4 integration depends on the user's installed simulator version.
        obs = {"events": [], "simulator": "cc4"}
        info = {"executed_action": action.action_name, "mode": action.mode}
        return StepResult(observation=obs, reward=0.0, terminated=terminated, truncated=False, info=info)
