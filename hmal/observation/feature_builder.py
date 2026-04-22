from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List

import numpy as np

from hmal.types import FeatureBundle
from hmal.observation.encoders import hashed_one_hot


FEATURE_GROUPS = ["host", "iface", "proc", "sess", "sys", "user"]


class FeatureBuilder:
    def __init__(self, hash_dim: int = 128, include_messages: bool = True):
        self.hash_dim = hash_dim
        self.include_messages = include_messages

    def _summarize_tokens(self, events: Iterable[Dict[str, Any]], keys: List[str]) -> Dict[str, float]:
        counter: Counter[str] = Counter()
        for event in events:
            for key in keys:
                if key in event and event[key] not in (None, ""):
                    counter[str(event[key])] += 1
        total = max(1, sum(counter.values()))
        return {k: v / total for k, v in counter.items()}

    def build(self, observation: Dict[str, Any], messages: List[int] | None = None) -> FeatureBundle:
        events = observation.get("events", [])
        bundle = FeatureBundle(
            host=self._summarize_tokens(events, ["hostname", "src_host", "dst_host", "zone"]),
            iface=self._summarize_tokens(events, ["src_ip", "dst_ip", "port", "protocol", "subnet"]),
            proc=self._summarize_tokens(events, ["process", "parent_process", "service"]),
            sess=self._summarize_tokens(events, ["session_id", "auth_type", "direction"]),
            sys=self._summarize_tokens(events, ["event_type", "status", "integrity", "host_role"]),
            user=self._summarize_tokens(events, ["user", "src_user", "dst_user", "domain"]),
            messages=messages or [],
        )
        return bundle

    def vectorize(self, bundle: FeatureBundle) -> np.ndarray:
        parts = []
        for group in FEATURE_GROUPS:
            mapping = getattr(bundle, group)
            tokens = [f"{group}:{k}:{round(v, 4)}" for k, v in sorted(mapping.items())]
            parts.append(hashed_one_hot(tokens, dim=self.hash_dim))
        if self.include_messages:
            msg_vec = np.array(bundle.messages[:8] + [0] * max(0, 8 - len(bundle.messages[:8])), dtype=np.float32)
            parts.append(msg_vec)
        return np.concatenate(parts, axis=0)
