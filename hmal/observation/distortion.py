from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Any, Deque, Dict, Iterable, List

import random


class DistortionChannel:
    def __init__(self, subsample_p: float = 0.0, dropout_p: float = 0.0, delay_steps: int = 0):
        self.subsample_p = subsample_p
        self.dropout_p = dropout_p
        self.delay_steps = delay_steps
        self.buffer: Deque[Dict[str, Any]] = deque()

    def _subsample(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [e for e in events if random.random() > self.subsample_p]

    def _drop_fields(self, event: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        for k, v in event.items():
            out[k] = None if random.random() < self.dropout_p else v
        return out

    def apply(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        obs = deepcopy(observation)
        events = obs.get("events", [])
        events = self._subsample(events)
        events = [self._drop_fields(e) for e in events]
        obs["events"] = events
        self.buffer.append(obs)
        if len(self.buffer) <= self.delay_steps:
            return {"events": []}
        return self.buffer.popleft()
