from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from hmal.types import ActionProposal, StepResult


class BaseCyberEnv(ABC):
    @abstractmethod
    def reset(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def step(self, action: ActionProposal) -> StepResult:
        raise NotImplementedError
