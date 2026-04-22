from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FeatureBundle:
    host: Dict[str, float] = field(default_factory=dict)
    iface: Dict[str, float] = field(default_factory=dict)
    proc: Dict[str, float] = field(default_factory=dict)
    sess: Dict[str, float] = field(default_factory=dict)
    sys: Dict[str, float] = field(default_factory=dict)
    user: Dict[str, float] = field(default_factory=dict)
    messages: List[int] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "iface": self.iface,
            "proc": self.proc,
            "sess": self.sess,
            "sys": self.sys,
            "user": self.user,
            "messages": self.messages,
        }


@dataclass
class StepResult:
    observation: Dict[str, Any]
    reward: float
    terminated: bool
    truncated: bool
    info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionProposal:
    mode: str
    action_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoalitionAllocation:
    method: str
    allocations: Dict[str, float]
