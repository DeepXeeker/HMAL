from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable

import yaml


ConfigDict = Dict[str, Any]


def load_yaml(path: str | Path) -> ConfigDict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config at {path} must be a YAML mapping.")
    return data


def deep_merge(base: ConfigDict, override: ConfigDict) -> ConfigDict:
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_many(paths: Iterable[str | Path]) -> ConfigDict:
    cfg: ConfigDict = {}
    for path in paths:
        cfg = deep_merge(cfg, load_yaml(path))
    return cfg
