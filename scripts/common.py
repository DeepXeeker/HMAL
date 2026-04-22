from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse

from hmal.config import load_many


def parser_with_common(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", required=True, help="Base config YAML")
    parser.add_argument("--env", required=True, help="Environment config YAML")
    return parser


def load_config_from_args(args) -> dict:
    return load_many([args.config, args.env])
