from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
from pathlib import Path

import pandas as pd

from hmal.data.darpa_tc import parse_jsonl_events, build_event_windows
from hmal.utils.io import ensure_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare DARPA TC E5 data")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--limit", type=int, default=10000)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = ensure_dir(args.output_dir)

    frames = []
    for path in sorted(input_dir.glob("*.jsonl")):
        frames.append(parse_jsonl_events(path, limit=args.limit))
    if not frames:
        raise FileNotFoundError("No JSONL files found. Convert DARPA TC E5 records to JSONL first.")
    events = pd.concat(frames, ignore_index=True, sort=False).fillna("")
    windows = build_event_windows(events)

    events.to_parquet(output_dir / "darpa_events.parquet", index=False)
    windows.to_parquet(output_dir / "darpa_windows.parquet", index=False)
    windows[["start", "end", "malicious"]].to_parquet(output_dir / "darpa_labels.parquet", index=False)
    print(f"Wrote {len(events)} events and {len(windows)} windows to {output_dir}")


if __name__ == "__main__":
    main()
