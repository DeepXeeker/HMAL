from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
from pathlib import Path

from hmal.config import load_many, load_yaml, deep_merge
from hmal.envs.offline_replay import OfflineReplayEnv
from hmal.training.pipeline import run_stage1, run_stage2, run_stage3, save_summary
from hmal.utils.io import ensure_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an ablation variant")
    parser.add_argument("--group", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--env", default="configs/env/lanl.yaml")
    args = parser.parse_args()

    cfg = load_many([args.config, args.env])
    ablation_cfg = load_yaml(f"configs/ablation/{args.group}.yaml")
    variant_cfg = ablation_cfg["variants"][args.variant]
    cfg = deep_merge(cfg, {"ablation": {"group": args.group, "variant": args.variant, **variant_cfg}})

    env_cfg = cfg["environment"]
    env = OfflineReplayEnv(
        processed_path=env_cfg.get("processed_path", ""),
        label_path=env_cfg.get("label_path"),
        episode_horizon=int(env_cfg.get("episode_horizon", 500)),
    )

    if args.group == "training_schedule":
        variant = cfg["ablation"]
        if variant.get("joint_end_to_end"):
            result = run_stage3(cfg, env)
        elif variant.get("reverse_order"):
            result = {"reverse_order": True, "stage2": run_stage2(cfg, env), "stage1": run_stage1(cfg, env)}
        elif variant.get("stage3"):
            result = run_stage3(cfg, env)
        else:
            result = {"stage1": run_stage1(cfg, env), "stage2": run_stage2(cfg, env)}
    elif args.group == "tier1_reward":
        cfg["selector"]["guidance_weight"] = float(cfg["ablation"].get("guidance_weight", cfg["selector"]["guidance_weight"]))
        cfg["selector"]["discount_option_credit"] = bool(cfg["ablation"].get("discount_option_credit", True))
        result = run_stage2(cfg, env)
    else:
        result = run_stage3(cfg, env)

    out_dir = ensure_dir(Path(cfg["experiment"]["output_dir"]) / "ablations" / args.group / args.variant)
    save_summary(out_dir / "summary.json", result)


if __name__ == "__main__":
    main()
