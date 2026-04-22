# Coalition-Aware HMAL

**Title: Coalition-Aware Autonomous Cyber Defense with Deception-Aware Hypergame Modeling and Hierarchical Multi-Agent Learning**

This repository implements:

- a **Tier-1 tabular Q-learning mode selector** over `Sense`, `Deceive`, `Recover`, and `Idle`
- **Tier-2 PPO executors** for mode-specific low-level actions
- **deception-aware observation corruption** for partial observability, delay, and dropout
- **coalition-aware message fusion**, budget enforcement, and core-feasibility checks
- **CC4/CybORG adapters** for interactive simulation
- **LANL** and **DARPA TC E5** offline replay pipelines for telemetry-driven evaluation
- **all ablation families described in the paper** as configurable experiments

## What is included

```text
coalition-aware-hmal/
├── configs/                  # default, env, and ablation configs
├── data_cards/               # dataset cards and preparation notes
├── docker/                   # reproducible container image
├── docs/                     # paper analysis, reconstruction notes, reproduction guide
├── hmal/                     # Python package
├── paper_results/            # CSVs containing reported paper values where available
├── scripts/                  # entry-point scripts for training, evaluation, ablations, plotting
├── tests/                    # lightweight unit tests
├── .github/workflows/        # CI
├── Makefile
├── pyproject.toml
└── requirements.txt
```

## Installation

### 1) Core Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 2) Optional: CybORG / CC4 simulator

This repository keeps CybORG optional because the simulator is distributed separately and is not available as a standard PyPI package for this project layout.

```bash
# after cloning the official CybORG / CC4 repository
pip install -e /path/to/CybORG-or-CC4-repo
```

The wrapper in `hmal/envs/cyborg_cc4.py` will raise a clear error if CybORG is not installed.

## Data preparation

### LANL cyber1

Place the official files under a directory such as:

```text
data/raw/lanl/
├── auth.txt.gz
├── proc.txt.gz
├── flows.txt.gz
├── dns.txt.gz
└── redteam.txt.gz
```

Then run:

```bash
python scripts/prepare_lanl.py --input-dir data/raw/lanl --output-dir data/processed/lanl
```

### DARPA Transparent Computing E5

This implementation expects either:

- pre-converted JSONL / CSV / Parquet files, or
- a user-supplied preprocessing step that exports normalized event records.

Then run:

```bash
python scripts/prepare_darpa.py --input-dir data/raw/darpa_tc_e5 --output-dir data/processed/darpa
```

## Training

### Stage I: Tier-2 PPO pretraining

```bash
python scripts/train_stage1.py --config configs/default.yaml --env configs/env/cc4.yaml
```

### Stage II: Tier-1 Q-learning

```bash
python scripts/train_stage2.py --config configs/default.yaml --env configs/env/cc4.yaml
```

### Stage III: joint refinement

```bash
python scripts/train_stage3.py --config configs/default.yaml --env configs/env/cc4.yaml
```

### End-to-end runner

```bash
python scripts/train_full.py --config configs/default.yaml --env configs/env/cc4.yaml
```

## Evaluation

```bash
python scripts/evaluate.py --config configs/default.yaml --env configs/env/lanl.yaml
python scripts/evaluate.py --config configs/default.yaml --env configs/env/darpa.yaml
```

## Ablations

All ablation groups from the paper are exposed as config families:

- hierarchy
- tier1_reward
- training_schedule
- coalition_fusion
- deception
- distortion
- feasibility

Example:

```bash
python scripts/run_ablation.py --group hierarchy --variant full_hmal
python scripts/run_ablation.py --group distortion --variant clean_training
```

## Testing

```bash
pytest -q
```

## License

MIT
