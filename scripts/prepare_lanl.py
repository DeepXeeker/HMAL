from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
from pathlib import Path

import pandas as pd

from hmal.data.lanl import parse_lanl_auth, parse_lanl_proc, parse_lanl_flows, parse_lanl_dns, build_event_windows
from hmal.utils.io import ensure_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare LANL cyber1 data")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = ensure_dir(args.output_dir)

    frames = []
    if (input_dir / "auth.txt.gz").exists():
        frames.append(parse_lanl_auth(input_dir / "auth.txt.gz", limit=args.limit))
    if (input_dir / "proc.txt.gz").exists():
        frames.append(parse_lanl_proc(input_dir / "proc.txt.gz", limit=args.limit))
    if (input_dir / "flows.txt.gz").exists():
        frames.append(parse_lanl_flows(input_dir / "flows.txt.gz", limit=args.limit))
    if (input_dir / "dns.txt.gz").exists():
        frames.append(parse_lanl_dns(input_dir / "dns.txt.gz", limit=args.limit))

    if not frames:
        raise FileNotFoundError("No LANL files were found in the input directory.")

    events = pd.concat(frames, ignore_index=True, sort=False).fillna("")
    windows = build_event_windows(events)

    events.to_parquet(output_dir / "lanl_events.parquet", index=False)
    windows.to_parquet(output_dir / "lanl_windows.parquet", index=False)
    windows[["start", "end", "malicious"]].to_parquet(output_dir / "lanl_labels.parquet", index=False)
    print(f"Wrote {len(events)} events and {len(windows)} windows to {output_dir}")


if __name__ == "__main__":
    main()
