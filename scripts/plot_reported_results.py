from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_numeric_table(path: Path, out_dir: Path) -> None:
    df = pd.read_csv(path)
    numeric_cols = [c for c in df.columns if c != df.columns[0] and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        return
    ax = df.plot(x=df.columns[0], y=numeric_cols, kind="bar", figsize=(10, 5))
    ax.set_title(path.stem)
    ax.set_xlabel(df.columns[0])
    ax.set_ylabel("value")
    plt.tight_layout()
    plt.savefig(out_dir / f"{path.stem}.png", dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot reported results")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    for csv_path in sorted(in_dir.glob("*.csv")):
        plot_numeric_table(csv_path, out_dir)


if __name__ == "__main__":
    main()
