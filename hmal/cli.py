from __future__ import annotations

import argparse
import json

from hmal.config import load_many


def main() -> None:
    parser = argparse.ArgumentParser(description="Coalition-aware HMAL CLI")
    parser.add_argument("configs", nargs="+", help="YAML config files to merge")
    args = parser.parse_args()
    cfg = load_many(args.configs)
    print(json.dumps(cfg, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
