from __future__ import annotations

from typing import Dict, Iterable, List


def pack_binary_message(flags: Iterable[int]) -> int:
    value = 0
    for idx, bit in enumerate(list(flags)[:8]):
        value |= (1 if bit else 0) << idx
    return value


def unpack_binary_message(value: int) -> List[int]:
    return [(value >> idx) & 1 for idx in range(8)]


def encode_semantic_message(payload: Dict[str, bool]) -> int:
    ordered_keys = [
        "red_seen",
        "critical_host",
        "lateral_move",
        "persistence",
        "service_disruption",
        "need_recovery",
        "decoy_hit",
        "budget_tight",
    ]
    return pack_binary_message([int(payload.get(key, False)) for key in ordered_keys])
