from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pathlib import Path

import numpy as np

from scripts.common import parser_with_common, load_config_from_args
from hmal.envs.offline_replay import OfflineReplayEnv
from hmal.evaluation.metrics import classification_metrics
from hmal.utils.io import dump_json, ensure_dir


def main() -> None:
    parser = parser_with_common("Evaluate HMAL on offline replay data")
    args = parser.parse_args()
    cfg = load_config_from_args(args)
    env_cfg = cfg["environment"]
    env = OfflineReplayEnv(
        processed_path=env_cfg.get("processed_path", ""),
        label_path=env_cfg.get("label_path"),
        episode_horizon=int(env_cfg.get("episode_horizon", 500)),
    )
    obs = env.reset()
    y_true = []
    y_score = []
    done = False
    while not done:
        score = float(obs.get("malicious", 0)) * 0.9 + 0.1
        y_true.append(int(obs.get("malicious", 0)))
        y_score.append(score)
        result = env.step(type("Action", (), {"mode": "Sense", "action_name": "Monitor", "parameters": {}})())
        obs = result.observation
        done = result.terminated or result.truncated
    metrics = classification_metrics(y_true, y_score)
    out_dir = ensure_dir(Path(cfg["experiment"]["output_dir"]) / "eval")
    dump_json(out_dir / f"eval_{env_cfg['type']}.json", metrics)
    print(metrics)


if __name__ == "__main__":
    main()
