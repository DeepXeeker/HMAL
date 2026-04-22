from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pathlib import Path

import pandas as pd


def main() -> None:
    root = Path("paper_results")
    for csv_path in sorted(root.glob("*.csv")):
        df = pd.read_csv(csv_path)
        print(f"
=== {csv_path.name} ===")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
