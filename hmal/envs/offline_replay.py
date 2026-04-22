from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from hmal.envs.base import BaseCyberEnv
from hmal.types import ActionProposal, StepResult


@dataclass
class OfflineReplayEnv(BaseCyberEnv):
    processed_path: str
    label_path: str | None = None
    episode_horizon: int = 500

    def __post_init__(self) -> None:
        path = Path(self.processed_path)
        if not path.exists():
            self.df = pd.DataFrame([
                {"time": i, "events": [{"event_type": "heartbeat", "hostname": f"host{i%5}", "user": f"u{i%3}"}], "malicious": int(i % 17 == 0)}
                for i in range(self.episode_horizon * 2)
            ])
        else:
            self.df = pd.read_parquet(path)
        self.index = 0

    def reset(self) -> Dict[str, Any]:
        self.index = 0
        row = self.df.iloc[self.index]
        return {"events": row["events"], "malicious": int(row.get("malicious", 0))}

    def step(self, action: ActionProposal) -> StepResult:
        row = self.df.iloc[self.index]
        malicious = int(row.get("malicious", 0))
        reward = 0.0
        if action.mode == "Sense":
            reward = 0.5 + 0.5 * malicious
        elif action.mode == "Deceive":
            reward = 0.25 + 0.75 * malicious
        elif action.mode == "Recover":
            reward = 1.0 * malicious - 0.2
        elif action.mode == "Idle":
            reward = 0.1 * (1 - malicious) - 0.1 * malicious

        self.index += 1
        terminated = self.index >= min(self.episode_horizon, len(self.df) - 1)
        next_row = self.df.iloc[min(self.index, len(self.df) - 1)]
        obs = {"events": next_row["events"], "malicious": int(next_row.get("malicious", 0))}
        info = {
            "mission_gain": reward,
            "risk_reduction": float(malicious and action.mode in {"Sense", "Recover", "Deceive"}),
            "projected_disruption": 0.2 if action.action_name in {"Restore", "BlockTrafficZone"} else 0.0,
        }
        return StepResult(observation=obs, reward=float(reward), terminated=terminated, truncated=False, info=info)
