from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.common import parser_with_common, load_config_from_args
from hmal.envs.offline_replay import OfflineReplayEnv
from hmal.training.pipeline import run_stage2, save_summary
from hmal.utils.io import ensure_dir


def main() -> None:
    parser = parser_with_common("Stage II Tier-1 training")
    args = parser.parse_args()
    cfg = load_config_from_args(args)
    env_cfg = cfg["environment"]
    env = OfflineReplayEnv(
        processed_path=env_cfg.get("processed_path", ""),
        label_path=env_cfg.get("label_path"),
        episode_horizon=int(env_cfg.get("episode_horizon", 500)),
    )
    result = run_stage2(cfg, env)
    out_dir = ensure_dir(Path(cfg["experiment"]["output_dir"]) / "stage2")
    save_summary(out_dir / "summary.json", result)


if __name__ == "__main__":
    main()
