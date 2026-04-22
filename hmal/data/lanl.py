from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

import gzip
import pandas as pd


def _safe_open(path: Path):
    return gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else open(path, "r", encoding="utf-8")


def parse_lanl_auth(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with _safe_open(path) as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            parts = line.strip().split(",")
            if len(parts) >= 9:
                rows.append(
                    {
                        "time": int(parts[0]),
                        "user": parts[1],
                        "dst_user": parts[2],
                        "src_host": parts[3],
                        "dst_host": parts[4],
                        "auth_type": parts[5],
                        "logon_type": parts[6],
                        "direction": parts[7],
                        "status": parts[8],
                        "event_type": "auth",
                    }
                )
    return pd.DataFrame(rows)


def parse_lanl_proc(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with _safe_open(path) as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            parts = line.strip().split(",")
            if len(parts) >= 5:
                rows.append(
                    {
                        "time": int(parts[0]),
                        "user": parts[1],
                        "hostname": parts[2],
                        "process": parts[3],
                        "status": parts[4],
                        "event_type": "proc",
                    }
                )
    return pd.DataFrame(rows)


def parse_lanl_flows(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with _safe_open(path) as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            parts = line.strip().split(",")
            if len(parts) >= 9:
                rows.append(
                    {
                        "time": int(parts[0]),
                        "duration": int(parts[1]),
                        "src_host": parts[2],
                        "src_port": parts[3],
                        "dst_host": parts[4],
                        "dst_port": parts[5],
                        "protocol": parts[6],
                        "packets": parts[7],
                        "bytes": parts[8],
                        "event_type": "flow",
                    }
                )
    return pd.DataFrame(rows)


def parse_lanl_dns(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with _safe_open(path) as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            parts = line.strip().split(",")
            if len(parts) >= 3:
                rows.append(
                    {
                        "time": int(parts[0]),
                        "src_host": parts[1],
                        "dst_host": parts[2],
                        "event_type": "dns",
                    }
                )
    return pd.DataFrame(rows)


def build_event_windows(df: pd.DataFrame, window_size: int = 128, step_size: int = 32) -> pd.DataFrame:
    df = df.sort_values("time").reset_index(drop=True)
    records = []
    for start in range(0, max(1, len(df) - window_size + 1), step_size):
        window = df.iloc[start : start + window_size]
        records.append(
            {
                "start": int(window["time"].min()),
                "end": int(window["time"].max()),
                "events": window.to_dict(orient="records"),
                "malicious": int((window.get("label", 0) == 1).any()) if "label" in window else 0,
            }
        )
    return pd.DataFrame(records)
