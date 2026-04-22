from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import json
import pandas as pd


def parse_jsonl_events(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            obj = json.loads(line)
            rows.append(
                {
                    "time": int(obj.get("timestamp", idx)),
                    "hostname": obj.get("host", obj.get("subject", "unknown")),
                    "user": obj.get("principal", "unknown"),
                    "process": obj.get("process_name", obj.get("predicateObjectPath", "unknown")),
                    "src_ip": obj.get("src_ip", ""),
                    "dst_ip": obj.get("dst_ip", ""),
                    "event_type": obj.get("type", "event"),
                    "label": int(obj.get("label", 0)),
                }
            )
    return pd.DataFrame(rows)


def build_event_windows(df: pd.DataFrame, window_size: int = 128, step_size: int = 32) -> pd.DataFrame:
    df = df.sort_values("time").reset_index(drop=True)
    rows = []
    for start in range(0, max(1, len(df) - window_size + 1), step_size):
        window = df.iloc[start : start + window_size]
        rows.append(
            {
                "start": int(window["time"].min()),
                "end": int(window["time"].max()),
                "events": window.to_dict(orient="records"),
                "malicious": int((window["label"] == 1).any()) if "label" in window else 0,
            }
        )
    return pd.DataFrame(rows)
