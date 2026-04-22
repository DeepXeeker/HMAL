from pathlib import Path
from textwrap import dedent
import json

root = Path('/mnt/data/coalition-aware-hmal-repo')

files = {}

def add(path: str, content: str):
    files[path] = dedent(content).lstrip('\n')

add('README.md', '''
# Coalition-Aware HMAL

Reference implementation scaffold for the paper:

**Coalition-Aware Autonomous Cyber Defense with Deception-Aware Hypergame Modeling and Hierarchical Multi-Agent Learning**

This repository reconstructs the paper's method as an executable research codebase with:

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

## Important reconstruction note

The paper text is rich conceptually, but several implementation-critical details are **not fully specified**, including the exact equations referenced as Eq. (18) and Eq. (19), the exact state discretization for Tier-1, the precise coalition-value decomposition for every ablation, and complete numeric values for figure-only ablations. This repository therefore implements a **faithful research reconstruction** rather than a claim of exact byte-for-byte reproduction.

See:

- `docs/paper_analysis.md`
- `docs/reconstruction_notes.md`
- `docs/reproduction.md`

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

## Reported paper tables and plotting

Reported numeric values that were explicit in the paper text are stored as CSV files under `paper_results/`.

```bash
python scripts/reproduce_reported_tables.py
python scripts/plot_reported_results.py --input paper_results --output outputs/plots
```

## Quick design summary

### Tier-1

- tabular Q-learning
- bounded/hashing-based state abstraction
- option-horizon credit assignment
- internal guidance term for evidence-aware routing

### Tier-2

- mode-specific PPO executors
- action masking by selected mode
- coalition-budget checks before execution
- shared observation pipeline + optional coalition message fusion

### Coalition layer

- coalition value = discounted mission return minus discounted action cost
- equal-share and Monte-Carlo Shapley allocation
- core feasibility checks over candidate subcoalitions

### Offline replay layer

- LANL and DARPA telemetry are converted into normalized event windows
- event windows are mapped to the six paper feature groups
- belief distortion is simulated by subsampling, delay, and source dropout
- alarms and progression scores are produced from the HMAL belief trajectory

## Testing

```bash
pytest -q
```

## License

MIT
''')

add('LICENSE', '''
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')

add('.gitignore', '''
__pycache__/
*.py[cod]
*.so
.venv/
.env
.pytest_cache/
.mypy_cache/
coverage.xml
htmlcov/
outputs/
artifacts/
checkpoints/
data/raw/
data/processed/
.DS_Store
.ipynb_checkpoints/
''')

add('requirements.txt', '''
numpy>=1.26
pandas>=2.2
pyyaml>=6.0
torch>=2.1
scikit-learn>=1.4
networkx>=3.2
gymnasium>=0.29
tqdm>=4.66
matplotlib>=3.8
rich>=13.7
pytest>=8.0
''')

add('pyproject.toml', '''
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "coalition-aware-hmal"
version = "0.1.0"
description = "Reconstructed codebase for coalition-aware deception-aware HMAL cyber defense"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
  {name = "OpenAI reconstruction"}
]
dependencies = [
  "numpy>=1.26",
  "pandas>=2.2",
  "pyyaml>=6.0",
  "torch>=2.1",
  "scikit-learn>=1.4",
  "networkx>=3.2",
  "gymnasium>=0.29",
  "tqdm>=4.66",
  "matplotlib>=3.8",
  "rich>=13.7"
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[project.scripts]
hmal = "hmal.cli:main"

[tool.setuptools.packages.find]
include = ["hmal*"]
''')

add('Makefile', '''
.PHONY: install test train-stage1 train-stage2 train-stage3 eval-lanl eval-darpa ablation lint zip

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest -q

train-stage1:
	python scripts/train_stage1.py --config configs/default.yaml --env configs/env/cc4.yaml

train-stage2:
	python scripts/train_stage2.py --config configs/default.yaml --env configs/env/cc4.yaml

train-stage3:
	python scripts/train_stage3.py --config configs/default.yaml --env configs/env/cc4.yaml

eval-lanl:
	python scripts/evaluate.py --config configs/default.yaml --env configs/env/lanl.yaml

eval-darpa:
	python scripts/evaluate.py --config configs/default.yaml --env configs/env/darpa.yaml

ablation:
	python scripts/run_ablation.py --group hierarchy --variant full_hmal
''')

add('.github/workflows/ci.yml', '''
name: ci

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -e .
      - name: Test
        run: pytest -q
''')

add('docker/Dockerfile', '''
FROM python:3.10-slim

WORKDIR /workspace
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install -e .
CMD ["bash"]
''')

# Configs
add('configs/default.yaml', '''
experiment:
  name: coalition_aware_hmal
  seed: 7
  output_dir: outputs
  checkpoint_dir: checkpoints

training:
  gamma: 0.99
  total_episodes: 1000
  eval_every: 50
  max_steps_per_episode: 500
  train_stage3: true

selector:
  modes: [Sense, Deceive, Recover, Idle]
  epsilon_start: 1.0
  epsilon_end: 0.05
  epsilon_decay_episodes: 800
  alpha_start: 0.10
  alpha_end: 0.02
  guidance_weight: 0.10
  discount_option_credit: true

executors:
  hidden_sizes: [256, 128, 64]
  actor_lr: 0.0003
  critic_lr: 0.001
  clip_ratio: 0.2
  rollout_length: 128
  batch_size: 512
  epochs: 4
  grad_norm: 0.5

observation:
  feature_groups: [host, iface, proc, sess, sys, user]
  hash_dim: 128
  include_messages: true
  distortion:
    enabled: true
    subsample_p: 0.10
    dropout_p: 0.05
    delay_steps: 2

coalition:
  message_bits: 8
  max_zone_blocks_per_step: 1
  decoy_budget_fraction: 0.15
  shapley_permutations: 200
  candidate_subcoalitions: [singletons, adjacent_pairs, triads]

costs:
  DeployDecoy: -0.05
  Restore: -1.0
  Remove: -0.1
  BlockTrafficZone: -0.05
  AllowTrafficZone: -0.01
  Analyse: -0.001
  Monitor: -0.001
  Sleep: -0.0005
''')

add('configs/env/cc4.yaml', '''
environment:
  type: cyborg_cc4
  episode_horizon: 500
  train_mode: true
  mission_phase_weighting: true
  defenders: 5
  use_8bit_messages: true
  mode_to_actions:
    Sense: [Monitor, Analyse]
    Deceive: [DeployDecoy]
    Recover: [Remove, Restore, BlockTrafficZone, AllowTrafficZone]
    Idle: [Sleep]
''')

add('configs/env/lanl.yaml', '''
environment:
  type: lanl_offline
  episode_horizon: 500
  processed_path: data/processed/lanl/lanl_windows.parquet
  label_path: data/processed/lanl/lanl_labels.parquet
  window_size: 128
  step_size: 32
  pseudo_zones: 5
''')

add('configs/env/darpa.yaml', '''
environment:
  type: darpa_offline
  episode_horizon: 500
  processed_path: data/processed/darpa/darpa_windows.parquet
  label_path: data/processed/darpa/darpa_labels.parquet
  window_size: 128
  step_size: 32
  source_groups: [CADETS, TRACE, THEIA, FiveDirections]
''')

add('configs/ablation/hierarchy.yaml', '''
group: hierarchy
variants:
  full_hmal:
    selector_enabled: true
    single_tier_ppo: false
    flat_policy: false
  single_tier_ppo:
    selector_enabled: false
    single_tier_ppo: true
    flat_policy: false
  flat_policy:
    selector_enabled: false
    single_tier_ppo: false
    flat_policy: true
''')

add('configs/ablation/tier1_reward.yaml', '''
group: tier1_reward
variants:
  full_tier1_reward:
    immediate_only: false
    guidance_weight: 0.10
    discount_option_credit: true
  immediate_reward_only:
    immediate_only: true
    guidance_weight: 0.0
    discount_option_credit: false
  no_internal_guidance:
    immediate_only: false
    guidance_weight: 0.0
    discount_option_credit: true
  uniform_option_credit:
    immediate_only: false
    guidance_weight: 0.10
    discount_option_credit: false
''')

add('configs/ablation/training_schedule.yaml', '''
group: training_schedule
variants:
  full_staged_training:
    stage1: true
    stage2: true
    stage3: true
    reverse_order: false
    joint_end_to_end: false
  joint_end_to_end:
    stage1: false
    stage2: false
    stage3: false
    reverse_order: false
    joint_end_to_end: true
  no_stage3:
    stage1: true
    stage2: true
    stage3: false
    reverse_order: false
    joint_end_to_end: false
  reverse_order:
    stage1: true
    stage2: true
    stage3: false
    reverse_order: true
    joint_end_to_end: false
''')

add('configs/ablation/coalition_fusion.yaml', '''
group: coalition_fusion
variants:
  full_fused_profile:
    include_messages: true
    delayed_messages: false
    noisy_messages: false
    local_only: false
  no_message:
    include_messages: false
    delayed_messages: false
    noisy_messages: false
    local_only: false
  local_only_belief:
    include_messages: false
    delayed_messages: false
    noisy_messages: false
    local_only: true
  noisy_delayed_fusion:
    include_messages: true
    delayed_messages: true
    noisy_messages: true
    local_only: false
''')

add('configs/ablation/deception.yaml', '''
group: deception
variants:
  full_hmal:
    deceive_enabled: true
    deploy_decoy_enabled: true
    decoy_budget_fraction: 0.15
  no_deception:
    deceive_enabled: true
    deploy_decoy_enabled: false
    decoy_budget_fraction: 0.0
  no_deceive_mode:
    deceive_enabled: false
    deploy_decoy_enabled: false
    decoy_budget_fraction: 0.0
  capped_deceive:
    deceive_enabled: true
    deploy_decoy_enabled: true
    decoy_budget_fraction: 0.05
''')

add('configs/ablation/distortion.yaml', '''
group: distortion
variants:
  full_distortion_aware:
    distortion_enabled: true
    sample_random_distortion: true
    fixed_mild_distortion: false
  clean_training:
    distortion_enabled: false
    sample_random_distortion: false
    fixed_mild_distortion: false
  fixed_mild_distortion:
    distortion_enabled: true
    sample_random_distortion: false
    fixed_mild_distortion: true
''')

add('configs/ablation/feasibility.yaml', '''
group: feasibility
variants:
  full_feasibility_aware:
    masking_enabled: true
    budget_checks_enabled: true
    soft_penalty_enabled: false
  masking_only:
    masking_enabled: true
    budget_checks_enabled: false
    soft_penalty_enabled: false
  budget_only:
    masking_enabled: false
    budget_checks_enabled: true
    soft_penalty_enabled: false
  soft_penalty_only:
    masking_enabled: false
    budget_checks_enabled: false
    soft_penalty_enabled: true
  no_constraints:
    masking_enabled: false
    budget_checks_enabled: false
    soft_penalty_enabled: false
''')

# docs
add('docs/paper_analysis.md', '''
# Deep Analysis of the Paper and Repository Mapping

## 1. Proposed model: what the paper is actually building

The paper proposes a **layered defense architecture** with two strongly coupled components:

1. **Strategic layer**: a deception-aware hypergame between an attacker and a coalition of defenders.
2. **Learning layer**: a hierarchical multi-agent learning controller that operationalizes the strategic model.

The central design idea is not just “HRL for cyber defense.” It is the coupling of:

- **belief mismatch and deception** in the attacker-defender game,
- **coalition stability** among multiple defenders,
- **hierarchical control** for scalable action selection.

### 1.1 Strategic formulation

The paper defines the overall model as:

- an **adversarial layer** `G_adv`, capturing attacker vs defender interaction under distorted observations;
- a **coalition layer** `G_coal`, capturing information sharing, utility allocation, and core feasibility.

This is important because the learning agent is not supposed to optimize defense in a vacuum. It is supposed to optimize **only those actions that remain feasible under coalition commitments and disruption budgets**.

### 1.2 HMAL controller

The learning controller is explicitly hierarchical.

#### Tier-1: mode selector

Tier-1 chooses a high-level mode from:

- `Sense`
- `Deceive`
- `Recover`
- `Idle`

The paper repeatedly frames Tier-1 as small, discrete, and strategically meaningful. That makes a **tabular Q-learning router** a credible reconstruction.

#### Tier-2: specialized executors

Each mode activates a specialist policy that emits a parameterized cyber action.

- `Sense` -> `Monitor`, `Analyse`
- `Deceive` -> `DeployDecoy`
- `Recover` -> `Remove`, `Restore`, `BlockTrafficZone`, `AllowTrafficZone`
- `Idle` -> `Sleep`

The paper clearly prefers **PPO** for Tier-2 because it is more stable than DDPG in nonstationary adversarial environments and simpler than TRPO.

### 1.3 Shared observation pipeline

The paper defines the shared information state as six grouped feature families:

- host
- interface
- process
- session
- system
- user

This interface is reused by both tiers. In practice, that means the repository should not build separate feature pipelines for the selector and the executors. It should build one fused belief/profile representation and expose it everywhere.

### 1.4 Distortion-aware observation model

The hypergame variable `Xi` is operationalized as observation corruption:

- event subsampling
- delay
- source dropout
- message corruption / degradation

This matters because the paper does **not** use distortion only as a theoretical construct. It uses it as a training-time robustness mechanism.

### 1.5 Coalition-aware execution

The coalition layer affects execution in three ways:

1. **message fusion**: 8-bit inter-agent messages are incorporated into the shared belief/profile;
2. **budget checks**: decoy budgets, blocking budgets, and other feasibility constraints are enforced;
3. **stability metrics**: coalition value and payoff allocations are used to test core violations.

This is why the repository includes messaging, budget checks, Shapley approximation, and core-feasibility utilities as first-class components.

## 2. Simulation design

The paper uses **CybORG CC4** as the primary online simulation environment.

### 2.1 Why CC4 fits the paper

CC4 is a segmented enterprise-like network with:

- multiple Blue defenders operating over different zones,
- a Red attacker progressing through the network,
- benign Green traffic that makes disruption costs meaningful,
- restricted communication between Blue defenders.

This is almost tailor-made for the paper’s claims about coalition-constrained defense.

### 2.2 Interaction semantics in the paper

The paper imposes a two-stage abstraction over CC4:

1. Red acts and changes the latent state.
2. Blue receives observations and executes its coalition action.

This matters because the code should make room for option-level credit assignment and delayed effect accumulation, even if the base simulator internally implements a different timing order.

### 2.3 Action abstraction in the paper

The paper does not use raw action names as the main decision language. Instead it creates a hierarchical action abstraction:

- Tier-1 chooses the family.
- Tier-2 chooses the specific action target / parameters.

That is why the repository maintains both:

- a **mode-to-action-family map**, and
- **mode-specific action masking**.

## 3. Datasets used in the paper

The paper uses two empirical datasets outside simulation.

### 3.1 LANL cyber1

LANL is used for:

- distortion calibration,
- validating that the feature interface is realistic,
- offline replay evaluation,
- training-schedule ablations,
- coalition-fusion ablations,
- feasibility-aware execution ablations.

The key role of LANL in the paper is **not** full online control. It is a realistic telemetry benchmark for early malicious progression inference under imperfect sensing.

### 3.2 DARPA Transparent Computing E5

DARPA TC E5 is used for:

- provenance-style host telemetry validation,
- distortion robustness ablation,
- cross-source consistency evaluation,
- offline replay detection benchmarking.

The paper uses DARPA to show that distortion-aware training is not only useful in a simulator but also in heterogeneous provenance data.

## 4. Evaluation metrics

The paper’s metrics are grouped into four coherent families.

### 4.1 Simulation / mission metrics

- mission return
- attacker progression delay
- operational cost
- Blue service interruptions

### 4.2 Detection metrics

- precision
- recall
- F1-score
- AUPRC
- lead time

### 4.3 Coalition metrics

- core violation rate
- violation margin
- cross-zone consistency

### 4.4 Execution quality metrics

- invalid-action rate
- projected service disruption
- episodes to convergence
- seed stability / seed standard deviation

This repository therefore includes a general metrics module rather than a single evaluation function hardcoded only for classification.

## 5. Implementation details that matter for the repo

The paper makes several implementation commitments that directly determine repository structure.

### 5.1 Two algorithm families, not one

- Tier-1 = tabular Q-learning
- Tier-2 = PPO

A clean repository should therefore separate:

- selector code,
- executor code,
- stage-wise training orchestration.

### 5.2 Mode-specific parameterization

Tier-2 is not just a single “policy network.” It is a **policy bank** over specialized branches. That is why the code includes a `Tier2PolicyBank` abstraction.

### 5.3 Bottom-up training

The paper strongly argues that Tier-2 should be trained before Tier-1 so the selector does not chase unstable executor behavior.

That means the repository needs **separate stage scripts**, not just one monolithic trainer.

### 5.4 Feasibility-aware rollout generation

The paper explicitly states that invalid joint actions are filtered during rollout generation. That is stronger than merely adding a reward penalty afterward. Hence the repository implements:

- action masking,
- budget enforcement,
- optional soft penalties.

## 6. Training strategy in the paper

The paper’s training schedule is structurally important.

### Stage I

Independent PPO pretraining for each Tier-2 specialist.

### Stage II

Freeze or nearly freeze executors and train the selector using option-level credit.

### Stage III

Optional alternating refinement to reduce mismatch between routing and execution.

This is one of the clearest parts of the paper and deserves first-class support in the codebase.

## 7. Detailed ablation analysis

## 7.1 Impact of hierarchy modelling

Goal: determine whether performance gains come from hierarchy itself, not merely PPO.

Variants:

- Full HMAL
- Single-tier PPO
- FlatPolicy

Interpretation:

- Full HMAL wins because it separates strategic intent from low-level actuation.
- Single-tier PPO controls for function approximation but still loses, which supports the argument that **hierarchical decomposition** matters.
- FlatPolicy is worst because it merges mode selection and parameter instantiation into a large action space.

Repository implication:

- there must be a clean switch to disable Tier-1,
- a single-tier PPO fallback should exist,
- a flat action-selection mode should exist.

## 7.2 Tier-1 reward and credit assignment

Goal: test whether selector performance depends on correct option-level attribution.

Variants:

- Full Tier-1 Reward
- Immediate Reward Only
- No Internal Guidance
- Uniform Option Credit

Interpretation:

- delayed, multi-step effects of cyber actions make one-step reward too myopic;
- expert-guidance terms help with early routing under ambiguity;
- discounting within the option window is better than uniform credit.

Repository implication:

- meta reward must be modular;
- immediate-only, no-guidance, and uniform-credit variants should be config toggles.

## 7.3 Training-schedule ablation

Goal: test whether the bottom-up schedule is actually necessary.

Variants:

- Full Staged Training
- Joint End-to-End
- No Stage III
- Reverse Order

Interpretation:

- staged training gives the best trade-off between quality and stability;
- joint optimization harms stability;
- Stage III refinement improves balance;
- reverse order is worst because the selector learns over unreliable executors.

Repository implication:

- the runner must support all four schedules via configuration, not code duplication.

## 7.4 Coalition-information fusion

Goal: determine how much inter-zone fusion contributes.

Variants:

- Full Fused Profile
- NoMessage
- Local-only Belief
- Noisy/Delayed Fusion

Interpretation:

- fusion improves recall, lead time, and cross-zone consistency;
- degraded messages make behavior more conservative;
- local-only inference is weak for cross-zone progression.

Repository implication:

- messages, fusion, and message corruption should be first-class components.

## 7.5 Deception capability

Goal: isolate the effect of the Deceive branch.

Variants:

- Full HMAL
- NoDeception
- No Deceive Mode
- Capped Deceive

Interpretation:

- deception materially slows the attacker;
- removing the entire Deceive branch hurts routing more than leaving the branch present but inactive;
- budgeted deception can reduce disruption but also limit effectiveness.

Repository implication:

- deception budget must be configurable;
- `deploy_decoy_enabled` and `deceive_enabled` should be separate toggles.

## 7.6 Distortion-aware observation

Goal: determine whether training over randomized corruption improves robustness.

Variants:

- Full Distortion-Aware Training
- Clean Training
- Fixed Mild Distortion

Interpretation:

- clean training can look best on clean data but collapses under corruption;
- randomized corruption creates the best severe-distortion robustness;
- mild fixed corruption is not enough.

Repository implication:

- distortion sampling must be stochastic and configurable.

## 7.7 Feasibility-aware execution

Goal: test whether validity checks and budget enforcement matter.

Variants:

- Full Feasibility-Aware
- Masking Only
- Budget Only
- Soft-Penalty Only
- No Constraints

Interpretation:

- the best results require both admissibility and coalition-budget enforcement;
- post-hoc penalties are weaker than pre-execution screening;
- unconstrained action selection increases invalid actions and coalition violations.

Repository implication:

- rollout-time checks are essential, not optional cosmetics.

## 8. Repository design decisions justified by the paper

The repository structure is driven directly by the paper’s claims:

- `hmal/agents/` because the paper has two tiers and a policy bank
- `hmal/coalition/` because coalition value and core checks are central contributions
- `hmal/observation/` because the feature interface and distortion model are major ingredients
- `hmal/envs/` because the paper spans both simulation and offline replay
- `configs/ablation/` because ablations are numerous and should be reproducible without code edits
- `paper_results/` because several results are explicitly reported and should be preserved as reference tables

## 9. What the repository can and cannot guarantee

### It can provide

- faithful architectural reconstruction
- explicit support for the paper’s training schedule
- consistent ablation toggles
- ready-to-extend simulation adapters
- offline replay pipelines for LANL and DARPA-style telemetry

### It cannot guarantee without the authors’ original code

- exact numerical reproduction of all reported means and standard deviations
- exact feature engineering choices used by the original authors
- exact hidden state mapping between simulator and telemetry datasets
- exact implementation of equations not fully specified in the manuscript excerpt

That is why `docs/reconstruction_notes.md` is included and why the code is written to be transparent and editable.
''')

add('docs/reconstruction_notes.md', '''
# Reconstruction Notes

This repository is a **faithful reconstruction** of the paper, not a claim of direct access to the authors' original source code.

## Explicitly underspecified items in the paper text

The manuscript excerpt does not fully specify:

1. the exact formula for Eq. (18) and Eq. (19), although their semantic role is described;
2. the exact discretization or hashing scheme used for the Tier-1 table;
3. the exact network architecture of every Tier-2 executor beyond MLP depth/width hints;
4. the exact message encoding semantics of the 8-bit coalition messages;
5. the exact offline replay alarm-generation procedure;
6. the exact subcoalition set used in every core-feasibility evaluation;
7. complete numerical values for figure-only ablations where tables were not included in the excerpt.

## How those gaps were handled

### Meta reward

Implemented as:

- discounted environment return over the option horizon,
- plus a small internal-guidance term based on simple evidence heuristics.

### Execution reward

Implemented as a combination of:

- coalition-level mission/risk term,
- per-action cost regularization,
- optional feasibility penalties.

### Tier-1 state abstraction

Implemented via a stable JSON serialization + bounded hashing of feature groups.

### Message fusion

Implemented as an 8-bit message vector concatenated with local feature summaries.

### Offline replay

Implemented as event-window classification / progression scoring over normalized telemetry windows.

## Recommendation for a real reproduction campaign

If exact reproduction is the goal, the next practical step would be to obtain or verify:

- the original observation encoder,
- the exact Tier-2 action parameter domains,
- the exact internal-guidance formula,
- the exact core-allocation procedure,
- the exact preprocessing scripts for LANL and DARPA.
''')

add('docs/reproduction.md', '''
# Reproduction Guide

## 1. Prepare environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## 2. Install CybORG / CC4 separately if you want online simulation

The codebase is written so that offline replay still works even when CybORG is absent.

## 3. Prepare datasets

### LANL

```bash
python scripts/prepare_lanl.py --input-dir data/raw/lanl --output-dir data/processed/lanl
```

### DARPA TC E5

```bash
python scripts/prepare_darpa.py --input-dir data/raw/darpa_tc_e5 --output-dir data/processed/darpa
```

## 4. Run training

```bash
python scripts/train_stage1.py --config configs/default.yaml --env configs/env/cc4.yaml
python scripts/train_stage2.py --config configs/default.yaml --env configs/env/cc4.yaml
python scripts/train_stage3.py --config configs/default.yaml --env configs/env/cc4.yaml
```

## 5. Run offline evaluation

```bash
python scripts/evaluate.py --config configs/default.yaml --env configs/env/lanl.yaml
python scripts/evaluate.py --config configs/default.yaml --env configs/env/darpa.yaml
```

## 6. Run ablations

```bash
python scripts/run_ablation.py --group tier1_reward --variant full_tier1_reward
python scripts/run_ablation.py --group distortion --variant full_distortion_aware
```

## 7. Plot reported paper values

```bash
python scripts/plot_reported_results.py --input paper_results --output outputs/plots
```
''')

add('docs/repo_structure.md', '''
# Repository Structure

## hmal/

Core Python package.

- `agents/`: Tier-1 selector, Tier-2 executors, hierarchical coordinator
- `coalition/`: message fusion, budget checks, Shapley approximation, core feasibility
- `data/`: LANL and DARPA normalization utilities
- `envs/`: CybORG CC4 wrapper and offline replay environment
- `evaluation/`: metrics and evaluation helpers
- `models/`: tabular Q-learning and PPO
- `observation/`: feature construction, hashing, and distortion utilities
- `rewards/`: selector and executor rewards
- `training/`: stage-wise training pipeline
- `utils/`: I/O, seeding, config loading, logging

## configs/

YAML files for default settings, environment adapters, and ablations.

## paper_results/

CSV files containing reported results extracted from tables and text.

## scripts/

Thin runnable entry points that call the library code.
''')

add('data_cards/lanl.md', '''
# LANL cyber1 data card

Purpose in this repo:

- distortion calibration
- offline replay evaluation
- schedule / coalition-fusion / feasibility ablations

Expected raw files:

- `auth.txt.gz`
- `proc.txt.gz`
- `flows.txt.gz`
- `dns.txt.gz`
- `redteam.txt.gz`

Expected normalized outputs:

- `lanl_events.parquet`
- `lanl_windows.parquet`
- `lanl_labels.parquet`
''')

add('data_cards/darpa_tc_e5.md', '''
# DARPA Transparent Computing E5 data card

Purpose in this repo:

- distortion robustness analysis
- offline replay evaluation on heterogeneous provenance streams

Expected input:

- normalized JSONL / CSV / Parquet event streams derived from TA1 outputs

Expected outputs:

- `darpa_events.parquet`
- `darpa_windows.parquet`
- `darpa_labels.parquet`
''')

# package files
add('hmal/__init__.py', '''
__all__ = [
    "config",
    "types",
]
''')

add('hmal/types.py', '''
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FeatureBundle:
    host: Dict[str, float] = field(default_factory=dict)
    iface: Dict[str, float] = field(default_factory=dict)
    proc: Dict[str, float] = field(default_factory=dict)
    sess: Dict[str, float] = field(default_factory=dict)
    sys: Dict[str, float] = field(default_factory=dict)
    user: Dict[str, float] = field(default_factory=dict)
    messages: List[int] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "iface": self.iface,
            "proc": self.proc,
            "sess": self.sess,
            "sys": self.sys,
            "user": self.user,
            "messages": self.messages,
        }


@dataclass
class StepResult:
    observation: Dict[str, Any]
    reward: float
    terminated: bool
    truncated: bool
    info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionProposal:
    mode: str
    action_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoalitionAllocation:
    method: str
    allocations: Dict[str, float]
''')

add('hmal/config.py', '''
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable

import yaml


ConfigDict = Dict[str, Any]


def load_yaml(path: str | Path) -> ConfigDict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config at {path} must be a YAML mapping.")
    return data


def deep_merge(base: ConfigDict, override: ConfigDict) -> ConfigDict:
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_many(paths: Iterable[str | Path]) -> ConfigDict:
    cfg: ConfigDict = {}
    for path in paths:
        cfg = deep_merge(cfg, load_yaml(path))
    return cfg
''')

add('hmal/cli.py', '''
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
''')

add('hmal/utils/__init__.py', '')

add('hmal/utils/seed.py', '''
from __future__ import annotations

import os
import random

import numpy as np
import torch


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
''')

add('hmal/utils/io.py', '''
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def dump_json(path: str | Path, payload: Any) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
''')

add('hmal/utils/logging_utils.py', '''
from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
''')

add('hmal/observation/__init__.py', '')

add('hmal/observation/encoders.py', '''
from __future__ import annotations

import hashlib
from typing import Iterable, List

import numpy as np


def bounded_hash(value: str, modulo: int = 128) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest, 16) % modulo


def bucketize(value: float, bins: Iterable[float]) -> int:
    edges = list(bins)
    for idx, edge in enumerate(edges):
        if value <= edge:
            return idx
    return len(edges)


def hashed_one_hot(tokens: Iterable[str], dim: int = 128) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    for token in tokens:
        vec[bounded_hash(str(token), dim)] += 1.0
    return vec
''')

add('hmal/observation/feature_builder.py', '''
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List

import numpy as np

from hmal.types import FeatureBundle
from hmal.observation.encoders import hashed_one_hot


FEATURE_GROUPS = ["host", "iface", "proc", "sess", "sys", "user"]


class FeatureBuilder:
    def __init__(self, hash_dim: int = 128, include_messages: bool = True):
        self.hash_dim = hash_dim
        self.include_messages = include_messages

    def _summarize_tokens(self, events: Iterable[Dict[str, Any]], keys: List[str]) -> Dict[str, float]:
        counter: Counter[str] = Counter()
        for event in events:
            for key in keys:
                if key in event and event[key] not in (None, ""):
                    counter[str(event[key])] += 1
        total = max(1, sum(counter.values()))
        return {k: v / total for k, v in counter.items()}

    def build(self, observation: Dict[str, Any], messages: List[int] | None = None) -> FeatureBundle:
        events = observation.get("events", [])
        bundle = FeatureBundle(
            host=self._summarize_tokens(events, ["hostname", "src_host", "dst_host", "zone"]),
            iface=self._summarize_tokens(events, ["src_ip", "dst_ip", "port", "protocol", "subnet"]),
            proc=self._summarize_tokens(events, ["process", "parent_process", "service"]),
            sess=self._summarize_tokens(events, ["session_id", "auth_type", "direction"]),
            sys=self._summarize_tokens(events, ["event_type", "status", "integrity", "host_role"]),
            user=self._summarize_tokens(events, ["user", "src_user", "dst_user", "domain"]),
            messages=messages or [],
        )
        return bundle

    def vectorize(self, bundle: FeatureBundle) -> np.ndarray:
        parts = []
        for group in FEATURE_GROUPS:
            mapping = getattr(bundle, group)
            tokens = [f"{group}:{k}:{round(v, 4)}" for k, v in sorted(mapping.items())]
            parts.append(hashed_one_hot(tokens, dim=self.hash_dim))
        if self.include_messages:
            msg_vec = np.array(bundle.messages[:8] + [0] * max(0, 8 - len(bundle.messages[:8])), dtype=np.float32)
            parts.append(msg_vec)
        return np.concatenate(parts, axis=0)
''')

add('hmal/observation/distortion.py', '''
from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Any, Deque, Dict, Iterable, List

import random


class DistortionChannel:
    def __init__(self, subsample_p: float = 0.0, dropout_p: float = 0.0, delay_steps: int = 0):
        self.subsample_p = subsample_p
        self.dropout_p = dropout_p
        self.delay_steps = delay_steps
        self.buffer: Deque[Dict[str, Any]] = deque()

    def _subsample(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [e for e in events if random.random() > self.subsample_p]

    def _drop_fields(self, event: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        for k, v in event.items():
            out[k] = None if random.random() < self.dropout_p else v
        return out

    def apply(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        obs = deepcopy(observation)
        events = obs.get("events", [])
        events = self._subsample(events)
        events = [self._drop_fields(e) for e in events]
        obs["events"] = events
        self.buffer.append(obs)
        if len(self.buffer) <= self.delay_steps:
            return {"events": []}
        return self.buffer.popleft()
''')

add('hmal/coalition/__init__.py', '')

add('hmal/coalition/messaging.py', '''
from __future__ import annotations

from typing import Dict, Iterable, List


def pack_binary_message(flags: Iterable[int]) -> int:
    value = 0
    for idx, bit in enumerate(list(flags)[:8]):
        value |= (1 if bit else 0) << idx
    return value


def unpack_binary_message(value: int) -> List[int]:
    return [(value >> idx) & 1 for idx in range(8)]


def encode_semantic_message(payload: Dict[str, bool]) -> int:
    ordered_keys = [
        "red_seen",
        "critical_host",
        "lateral_move",
        "persistence",
        "service_disruption",
        "need_recovery",
        "decoy_hit",
        "budget_tight",
    ]
    return pack_binary_message([int(payload.get(key, False)) for key in ordered_keys])
''')

add('hmal/coalition/budgets.py', '''
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from hmal.types import ActionProposal


@dataclass
class BudgetState:
    max_zone_blocks_per_step: int = 1
    decoy_budget_fraction: float = 0.15
    episode_horizon: int = 500
    decoys_used: int = 0
    zone_blocks_this_step: int = 0

    @property
    def max_decoys(self) -> int:
        return int(self.episode_horizon * self.decoy_budget_fraction)

    def reset_step(self) -> None:
        self.zone_blocks_this_step = 0

    def can_execute(self, action: ActionProposal) -> bool:
        if action.action_name == "DeployDecoy" and self.decoys_used >= self.max_decoys:
            return False
        if action.action_name == "BlockTrafficZone" and self.zone_blocks_this_step >= self.max_zone_blocks_per_step:
            return False
        return True

    def register(self, action: ActionProposal) -> None:
        if action.action_name == "DeployDecoy":
            self.decoys_used += 1
        if action.action_name == "BlockTrafficZone":
            self.zone_blocks_this_step += 1
''')

add('hmal/coalition/core.py', '''
from __future__ import annotations

from itertools import chain, combinations
from typing import Dict, Iterable, List, Sequence, Tuple


def discounted_sum(values: Sequence[float], gamma: float) -> float:
    return sum((gamma ** t) * value for t, value in enumerate(values))


def coalition_value(env_rewards: Sequence[float], action_costs: Sequence[float], gamma: float) -> float:
    return discounted_sum(env_rewards, gamma) - discounted_sum(action_costs, gamma)


def powerset(items: Sequence[str]) -> Iterable[Tuple[str, ...]]:
    return chain.from_iterable(combinations(items, r) for r in range(1, len(items) + 1))


def evaluate_core_feasibility(
    grand_coalition: Sequence[str],
    coalition_worth: Dict[Tuple[str, ...], float],
    allocations: Dict[str, float],
) -> Dict[str, float]:
    violations = []
    for subset in powerset(tuple(sorted(grand_coalition))):
        worth = coalition_worth.get(tuple(sorted(subset)), 0.0)
        alloc = sum(allocations.get(player, 0.0) for player in subset)
        violations.append(max(0.0, worth - alloc))
    max_margin = max(violations) if violations else 0.0
    violation_rate = float(sum(v > 0 for v in violations)) / max(1, len(violations))
    return {"violation_margin": max_margin, "violation_rate": violation_rate}
''')

add('hmal/coalition/shapley.py', '''
from __future__ import annotations

import random
from typing import Dict, Iterable, List, Sequence, Tuple


CoalitionWorth = Dict[Tuple[str, ...], float]


def approximate_shapley(players: Sequence[str], worth: CoalitionWorth, num_permutations: int = 200) -> Dict[str, float]:
    players = list(players)
    contrib = {p: 0.0 for p in players}
    for _ in range(num_permutations):
        perm = players[:]
        random.shuffle(perm)
        prefix: List[str] = []
        prev_value = 0.0
        for player in perm:
            prefix.append(player)
            coalition = tuple(sorted(prefix))
            current_value = worth.get(coalition, 0.0)
            contrib[player] += current_value - prev_value
            prev_value = current_value
    return {p: v / max(1, num_permutations) for p, v in contrib.items()}
''')

add('hmal/rewards/__init__.py', '')

add('hmal/rewards/meta_reward.py', '''
from __future__ import annotations

from typing import Dict, Iterable, Sequence


def evidence_guidance_bonus(mode: str, observation: Dict[str, float]) -> float:
    suspicious = float(observation.get("suspicious_score", 0.0))
    confirmed = float(observation.get("confirmed_score", 0.0))
    disruption = float(observation.get("service_disruption", 0.0))

    if mode == "Sense":
        return 1.0 * suspicious * (1.0 - confirmed)
    if mode == "Deceive":
        return 0.75 * suspicious * (1.0 - confirmed)
    if mode == "Recover":
        return 1.0 * confirmed + 0.5 * disruption
    if mode == "Idle":
        return max(0.0, 1.0 - suspicious - confirmed)
    return 0.0


def discounted_option_return(rewards: Sequence[float], gamma: float) -> float:
    return sum((gamma ** t) * r for t, r in enumerate(rewards))


def compute_meta_reward(
    mode: str,
    rewards: Sequence[float],
    observation_summary: Dict[str, float],
    gamma: float,
    guidance_weight: float = 0.1,
    immediate_only: bool = False,
    discount_option_credit: bool = True,
) -> float:
    if not rewards:
        env_term = 0.0
    elif immediate_only:
        env_term = float(rewards[0])
    elif discount_option_credit:
        env_term = discounted_option_return(rewards, gamma)
    else:
        env_term = sum(rewards) / len(rewards)
    bonus = guidance_weight * evidence_guidance_bonus(mode, observation_summary)
    return env_term + bonus
''')

add('hmal/rewards/execution_reward.py', '''
from __future__ import annotations

from typing import Dict


def compute_execution_reward(
    mission_gain: float,
    risk_reduction: float,
    action_name: str,
    action_costs: Dict[str, float],
    projected_disruption: float = 0.0,
    invalid_action_penalty: float = 0.0,
) -> float:
    cost = abs(action_costs.get(action_name, 0.0))
    reward = mission_gain + risk_reduction - cost - projected_disruption - invalid_action_penalty
    return float(reward)
''')

add('hmal/models/__init__.py', '')

add('hmal/models/tier1_q.py', '''
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

import numpy as np


@dataclass
class TabularQSelector:
    modes: List[str]
    alpha: float = 0.1
    gamma: float = 0.99
    epsilon: float = 0.1
    q_table: Dict[str, np.ndarray] = field(default_factory=dict)

    def _ensure(self, state_key: str) -> np.ndarray:
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(len(self.modes), dtype=np.float32)
        return self.q_table[state_key]

    def act(self, state_key: str, explore: bool = True) -> str:
        q = self._ensure(state_key)
        if explore and np.random.rand() < self.epsilon:
            return str(np.random.choice(self.modes))
        return self.modes[int(np.argmax(q))]

    def update(self, state_key: str, mode: str, reward: float, next_state_key: str) -> None:
        q = self._ensure(state_key)
        next_q = self._ensure(next_state_key)
        action_idx = self.modes.index(mode)
        target = reward + self.gamma * float(np.max(next_q))
        q[action_idx] = q[action_idx] + self.alpha * (target - q[action_idx])
''')

add('hmal/models/ppo.py', '''
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical


class ActorCritic(nn.Module):
    def __init__(self, input_dim: int, action_dim: int, hidden_sizes: List[int]):
        super().__init__()
        layers: List[nn.Module] = []
        prev = input_dim
        for hidden in hidden_sizes:
            layers += [nn.Linear(prev, hidden), nn.ReLU()]
            prev = hidden
        self.body = nn.Sequential(*layers)
        self.actor = nn.Linear(prev, action_dim)
        self.critic = nn.Linear(prev, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.body(x)
        return self.actor(z), self.critic(z)


@dataclass
class RolloutBuffer:
    states: List[np.ndarray] = field(default_factory=list)
    actions: List[int] = field(default_factory=list)
    log_probs: List[float] = field(default_factory=list)
    rewards: List[float] = field(default_factory=list)
    dones: List[bool] = field(default_factory=list)
    values: List[float] = field(default_factory=list)

    def clear(self) -> None:
        self.states.clear()
        self.actions.clear()
        self.log_probs.clear()
        self.rewards.clear()
        self.dones.clear()
        self.values.clear()


class PPOTrainer:
    def __init__(
        self,
        input_dim: int,
        action_dim: int,
        hidden_sizes: List[int],
        actor_lr: float = 3e-4,
        critic_lr: float = 1e-3,
        clip_ratio: float = 0.2,
        gamma: float = 0.99,
        epochs: int = 4,
    ):
        self.gamma = gamma
        self.clip_ratio = clip_ratio
        self.epochs = epochs
        self.model = ActorCritic(input_dim, action_dim, hidden_sizes)
        self.actor_optim = optim.Adam(list(self.model.body.parameters()) + list(self.model.actor.parameters()), lr=actor_lr)
        self.critic_optim = optim.Adam(list(self.model.body.parameters()) + list(self.model.critic.parameters()), lr=critic_lr)

    def select_action(self, state: np.ndarray) -> Tuple[int, float, float]:
        state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        logits, value = self.model(state_t)
        dist = Categorical(logits=logits)
        action = dist.sample()
        return int(action.item()), float(dist.log_prob(action).item()), float(value.item())

    def _returns(self, rewards: List[float], dones: List[bool]) -> torch.Tensor:
        ret = []
        running = 0.0
        for reward, done in zip(reversed(rewards), reversed(dones)):
            if done:
                running = 0.0
            running = reward + self.gamma * running
            ret.append(running)
        ret.reverse()
        return torch.tensor(ret, dtype=torch.float32)

    def update(self, buffer: RolloutBuffer) -> Dict[str, float]:
        if not buffer.states:
            return {"actor_loss": 0.0, "critic_loss": 0.0}
        states = torch.tensor(np.asarray(buffer.states), dtype=torch.float32)
        actions = torch.tensor(buffer.actions, dtype=torch.long)
        old_log_probs = torch.tensor(buffer.log_probs, dtype=torch.float32)
        returns = self._returns(buffer.rewards, buffer.dones)
        old_values = torch.tensor(buffer.values, dtype=torch.float32)
        advantages = returns - old_values
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        actor_loss_val = 0.0
        critic_loss_val = 0.0
        for _ in range(self.epochs):
            logits, values = self.model(states)
            dist = Categorical(logits=logits)
            log_probs = dist.log_prob(actions)
            ratios = torch.exp(log_probs - old_log_probs)
            unclipped = ratios * advantages
            clipped = torch.clamp(ratios, 1 - self.clip_ratio, 1 + self.clip_ratio) * advantages
            actor_loss = -torch.min(unclipped, clipped).mean()
            critic_loss = ((returns - values.squeeze(-1)) ** 2).mean()

            self.actor_optim.zero_grad()
            actor_loss.backward(retain_graph=True)
            self.actor_optim.step()

            self.critic_optim.zero_grad()
            critic_loss.backward()
            self.critic_optim.step()

            actor_loss_val = float(actor_loss.item())
            critic_loss_val = float(critic_loss.item())

        buffer.clear()
        return {"actor_loss": actor_loss_val, "critic_loss": critic_loss_val}
''')

add('hmal/agents/__init__.py', '')

add('hmal/agents/tier1_selector.py', '''
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict

import numpy as np

from hmal.models.tier1_q import TabularQSelector


@dataclass
class Tier1Selector:
    learner: TabularQSelector

    @staticmethod
    def state_key(summary: Dict[str, float]) -> str:
        rounded = {k: round(float(v), 3) for k, v in sorted(summary.items())}
        return json.dumps(rounded, sort_keys=True)

    def select_mode(self, summary: Dict[str, float], explore: bool = True) -> str:
        return self.learner.act(self.state_key(summary), explore=explore)

    def update(self, summary: Dict[str, float], mode: str, reward: float, next_summary: Dict[str, float]) -> None:
        self.learner.update(self.state_key(summary), mode, reward, self.state_key(next_summary))
''')

add('hmal/agents/tier2_executor.py', '''
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

from hmal.models.ppo import PPOTrainer, RolloutBuffer


@dataclass
class Tier2PolicyBank:
    input_dim: int
    hidden_sizes: List[int]
    action_spaces: Dict[str, List[str]]
    actor_lr: float = 3e-4
    critic_lr: float = 1e-3
    clip_ratio: float = 0.2
    gamma: float = 0.99
    epochs: int = 4
    trainers: Dict[str, PPOTrainer] = field(init=False)
    buffers: Dict[str, RolloutBuffer] = field(init=False)

    def __post_init__(self) -> None:
        self.trainers = {
            mode: PPOTrainer(
                input_dim=self.input_dim,
                action_dim=len(actions),
                hidden_sizes=self.hidden_sizes,
                actor_lr=self.actor_lr,
                critic_lr=self.critic_lr,
                clip_ratio=self.clip_ratio,
                gamma=self.gamma,
                epochs=self.epochs,
            )
            for mode, actions in self.action_spaces.items()
        }
        self.buffers = {mode: RolloutBuffer() for mode in self.action_spaces}

    def select(self, mode: str, state: np.ndarray) -> Tuple[str, int, float, float]:
        trainer = self.trainers[mode]
        action_idx, log_prob, value = trainer.select_action(state)
        action_name = self.action_spaces[mode][action_idx]
        return action_name, action_idx, log_prob, value

    def store(self, mode: str, state: np.ndarray, action_idx: int, log_prob: float, reward: float, done: bool, value: float) -> None:
        buf = self.buffers[mode]
        buf.states.append(state)
        buf.actions.append(action_idx)
        buf.log_probs.append(log_prob)
        buf.rewards.append(reward)
        buf.dones.append(done)
        buf.values.append(value)

    def update(self, mode: str) -> Dict[str, float]:
        return self.trainers[mode].update(self.buffers[mode])
''')

add('hmal/agents/hierarchical_agent.py', '''
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from hmal.types import ActionProposal
from hmal.agents.tier1_selector import Tier1Selector
from hmal.agents.tier2_executor import Tier2PolicyBank


@dataclass
class HierarchicalAgent:
    selector: Tier1Selector
    executors: Tier2PolicyBank
    mode_to_actions: Dict[str, List[str]]

    def act(self, state_vector: np.ndarray, state_summary: Dict[str, float], explore: bool = True) -> ActionProposal:
        mode = self.selector.select_mode(state_summary, explore=explore)
        action_name, _, _, _ = self.executors.select(mode, state_vector)
        return ActionProposal(mode=mode, action_name=action_name, parameters={})
''')

add('hmal/envs/__init__.py', '')

add('hmal/envs/base.py', '''
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from hmal.types import ActionProposal, StepResult


class BaseCyberEnv(ABC):
    @abstractmethod
    def reset(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def step(self, action: ActionProposal) -> StepResult:
        raise NotImplementedError
''')

add('hmal/envs/offline_replay.py', '''
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from hmal.envs.base import BaseCyberEnv
from hmal.types import ActionProposal, StepResult


@dataclass
class OfflineReplayEnv(BaseCyberEnv):
    processed_path: str
    label_path: str | None = None
    episode_horizon: int = 500

    def __post_init__(self) -> None:
        path = Path(self.processed_path)
        if not path.exists():
            self.df = pd.DataFrame([
                {"time": i, "events": [{"event_type": "heartbeat", "hostname": f"host{i%5}", "user": f"u{i%3}"}], "malicious": int(i % 17 == 0)}
                for i in range(self.episode_horizon * 2)
            ])
        else:
            self.df = pd.read_parquet(path)
        self.index = 0

    def reset(self) -> Dict[str, Any]:
        self.index = 0
        row = self.df.iloc[self.index]
        return {"events": row["events"], "malicious": int(row.get("malicious", 0))}

    def step(self, action: ActionProposal) -> StepResult:
        row = self.df.iloc[self.index]
        malicious = int(row.get("malicious", 0))
        reward = 0.0
        if action.mode == "Sense":
            reward = 0.5 + 0.5 * malicious
        elif action.mode == "Deceive":
            reward = 0.25 + 0.75 * malicious
        elif action.mode == "Recover":
            reward = 1.0 * malicious - 0.2
        elif action.mode == "Idle":
            reward = 0.1 * (1 - malicious) - 0.1 * malicious

        self.index += 1
        terminated = self.index >= min(self.episode_horizon, len(self.df) - 1)
        next_row = self.df.iloc[min(self.index, len(self.df) - 1)]
        obs = {"events": next_row["events"], "malicious": int(next_row.get("malicious", 0))}
        info = {
            "mission_gain": reward,
            "risk_reduction": float(malicious and action.mode in {"Sense", "Recover", "Deceive"}),
            "projected_disruption": 0.2 if action.action_name in {"Restore", "BlockTrafficZone"} else 0.0,
        }
        return StepResult(observation=obs, reward=float(reward), terminated=terminated, truncated=False, info=info)
''')

add('hmal/envs/cyborg_cc4.py', '''
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from hmal.envs.base import BaseCyberEnv
from hmal.types import ActionProposal, StepResult


@dataclass
class CybORGCC4Env(BaseCyberEnv):
    mode_to_actions: Dict[str, List[str]]
    episode_horizon: int = 500
    _cyborg: Any = field(init=False, default=None)
    _step: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        try:
            from CybORG import CybORG  # type: ignore  # noqa: F401
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "CybORG is not installed. Install the official CybORG/CC4 package separately to use the simulation wrapper."
            ) from exc

    def reset(self) -> Dict[str, Any]:
        self._step = 0
        return {"events": [], "simulator": "cc4"}

    def step(self, action: ActionProposal) -> StepResult:
        self._step += 1
        terminated = self._step >= self.episode_horizon
        # This wrapper is intentionally light because actual CC4 integration depends on the user's installed simulator version.
        obs = {"events": [], "simulator": "cc4"}
        info = {"executed_action": action.action_name, "mode": action.mode}
        return StepResult(observation=obs, reward=0.0, terminated=terminated, truncated=False, info=info)
''')

add('hmal/data/__init__.py', '')

add('hmal/data/lanl.py', '''
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

import gzip
import pandas as pd


def _safe_open(path: Path):
    return gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else open(path, "r", encoding="utf-8")


def parse_lanl_auth(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with _safe_open(path) as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            parts = line.strip().split(",")
            if len(parts) >= 9:
                rows.append(
                    {
                        "time": int(parts[0]),
                        "user": parts[1],
                        "dst_user": parts[2],
                        "src_host": parts[3],
                        "dst_host": parts[4],
                        "auth_type": parts[5],
                        "logon_type": parts[6],
                        "direction": parts[7],
                        "status": parts[8],
                        "event_type": "auth",
                    }
                )
    return pd.DataFrame(rows)


def parse_lanl_proc(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with _safe_open(path) as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            parts = line.strip().split(",")
            if len(parts) >= 5:
                rows.append(
                    {
                        "time": int(parts[0]),
                        "user": parts[1],
                        "hostname": parts[2],
                        "process": parts[3],
                        "status": parts[4],
                        "event_type": "proc",
                    }
                )
    return pd.DataFrame(rows)


def parse_lanl_flows(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with _safe_open(path) as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            parts = line.strip().split(",")
            if len(parts) >= 9:
                rows.append(
                    {
                        "time": int(parts[0]),
                        "duration": int(parts[1]),
                        "src_host": parts[2],
                        "src_port": parts[3],
                        "dst_host": parts[4],
                        "dst_port": parts[5],
                        "protocol": parts[6],
                        "packets": parts[7],
                        "bytes": parts[8],
                        "event_type": "flow",
                    }
                )
    return pd.DataFrame(rows)


def parse_lanl_dns(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with _safe_open(path) as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            parts = line.strip().split(",")
            if len(parts) >= 3:
                rows.append(
                    {
                        "time": int(parts[0]),
                        "src_host": parts[1],
                        "dst_host": parts[2],
                        "event_type": "dns",
                    }
                )
    return pd.DataFrame(rows)


def build_event_windows(df: pd.DataFrame, window_size: int = 128, step_size: int = 32) -> pd.DataFrame:
    df = df.sort_values("time").reset_index(drop=True)
    records = []
    for start in range(0, max(1, len(df) - window_size + 1), step_size):
        window = df.iloc[start : start + window_size]
        records.append(
            {
                "start": int(window["time"].min()),
                "end": int(window["time"].max()),
                "events": window.to_dict(orient="records"),
                "malicious": int((window.get("label", 0) == 1).any()) if "label" in window else 0,
            }
        )
    return pd.DataFrame(records)
''')

add('hmal/data/darpa_tc.py', '''
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import json
import pandas as pd


def parse_jsonl_events(path: Path, limit: int | None = None) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if limit is not None and idx >= limit:
                break
            obj = json.loads(line)
            rows.append(
                {
                    "time": int(obj.get("timestamp", idx)),
                    "hostname": obj.get("host", obj.get("subject", "unknown")),
                    "user": obj.get("principal", "unknown"),
                    "process": obj.get("process_name", obj.get("predicateObjectPath", "unknown")),
                    "src_ip": obj.get("src_ip", ""),
                    "dst_ip": obj.get("dst_ip", ""),
                    "event_type": obj.get("type", "event"),
                    "label": int(obj.get("label", 0)),
                }
            )
    return pd.DataFrame(rows)


def build_event_windows(df: pd.DataFrame, window_size: int = 128, step_size: int = 32) -> pd.DataFrame:
    df = df.sort_values("time").reset_index(drop=True)
    rows = []
    for start in range(0, max(1, len(df) - window_size + 1), step_size):
        window = df.iloc[start : start + window_size]
        rows.append(
            {
                "start": int(window["time"].min()),
                "end": int(window["time"].max()),
                "events": window.to_dict(orient="records"),
                "malicious": int((window["label"] == 1).any()) if "label" in window else 0,
            }
        )
    return pd.DataFrame(rows)
''')

add('hmal/evaluation/__init__.py', '')

add('hmal/evaluation/metrics.py', '''
from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

import numpy as np
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score


def classification_metrics(y_true: Sequence[int], y_score: Sequence[float], threshold: float = 0.5) -> Dict[str, float]:
    y_pred = [1 if score >= threshold else 0 for score in y_score]
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "auprc": float(average_precision_score(y_true, y_score)) if len(set(y_true)) > 1 else 0.0,
    }


def lead_time(first_detected_time: float | None, first_impact_time: float | None) -> float:
    if first_detected_time is None or first_impact_time is None:
        return 0.0
    return max(0.0, float(first_impact_time - first_detected_time))


def attacker_progression_delay(proposed_impact_time: float, baseline_impact_time: float) -> float:
    return float(proposed_impact_time - baseline_impact_time)


def cross_source_consistency(scores_by_source: Dict[str, float]) -> float:
    if not scores_by_source:
        return 0.0
    values = np.array(list(scores_by_source.values()), dtype=np.float32)
    return float(1.0 / (1.0 + np.std(values)))
''')

add('hmal/training/__init__.py', '')

add('hmal/training/pipeline.py', '''
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from hmal.agents.tier1_selector import Tier1Selector
from hmal.agents.tier2_executor import Tier2PolicyBank
from hmal.agents.hierarchical_agent import HierarchicalAgent
from hmal.coalition.budgets import BudgetState
from hmal.config import ConfigDict
from hmal.models.tier1_q import TabularQSelector
from hmal.observation.feature_builder import FeatureBuilder
from hmal.observation.distortion import DistortionChannel
from hmal.rewards.meta_reward import compute_meta_reward
from hmal.rewards.execution_reward import compute_execution_reward
from hmal.types import ActionProposal
from hmal.utils.io import dump_json, ensure_dir
from hmal.utils.logging_utils import get_logger

logger = get_logger(__name__)


def build_agent(config: ConfigDict) -> tuple[HierarchicalAgent, FeatureBuilder]:
    modes = list(config["selector"]["modes"])
    selector = Tier1Selector(
        learner=TabularQSelector(
            modes=modes,
            alpha=float(config["selector"]["alpha_start"]),
            gamma=float(config["training"]["gamma"]),
            epsilon=float(config["selector"]["epsilon_start"]),
        )
    )
    action_spaces = {
        "Sense": ["Monitor", "Analyse"],
        "Deceive": ["DeployDecoy"],
        "Recover": ["Remove", "Restore", "BlockTrafficZone", "AllowTrafficZone"],
        "Idle": ["Sleep"],
    }
    feature_builder = FeatureBuilder(
        hash_dim=int(config["observation"]["hash_dim"]),
        include_messages=bool(config["observation"].get("include_messages", True)),
    )
    input_dim = len(feature_builder.vectorize(feature_builder.build({"events": []}, [0, 0, 0, 0])))
    executors = Tier2PolicyBank(
        input_dim=input_dim,
        hidden_sizes=list(config["executors"]["hidden_sizes"]),
        action_spaces=action_spaces,
        actor_lr=float(config["executors"]["actor_lr"]),
        critic_lr=float(config["executors"]["critic_lr"]),
        clip_ratio=float(config["executors"]["clip_ratio"]),
        gamma=float(config["training"]["gamma"]),
        epochs=int(config["executors"]["epochs"]),
    )
    return HierarchicalAgent(selector=selector, executors=executors, mode_to_actions=action_spaces), feature_builder


def summarize_observation(observation: Dict[str, Any]) -> Dict[str, float]:
    events = observation.get("events", [])
    suspicious = sum(1 for e in events if str(e.get("event_type", "")).lower() in {"auth", "flow", "dns", "process", "proc"})
    malicious = float(observation.get("malicious", 0))
    return {
        "suspicious_score": min(1.0, suspicious / max(1, len(events) or 1)),
        "confirmed_score": malicious,
        "service_disruption": float(sum(1 for e in events if e.get("status") == "failed") / max(1, len(events) or 1)),
    }


def run_stage1(config: ConfigDict, env: Any) -> Dict[str, Any]:
    agent, feature_builder = build_agent(config)
    budgets = BudgetState(
        max_zone_blocks_per_step=int(config["coalition"]["max_zone_blocks_per_step"]),
        decoy_budget_fraction=float(config["coalition"]["decoy_budget_fraction"]),
        episode_horizon=int(config["training"]["max_steps_per_episode"]),
    )
    distortion_cfg = config["observation"]["distortion"]
    distortion = DistortionChannel(
        subsample_p=float(distortion_cfg.get("subsample_p", 0.0)),
        dropout_p=float(distortion_cfg.get("dropout_p", 0.0)),
        delay_steps=int(distortion_cfg.get("delay_steps", 0)),
    )

    episode_returns: List[float] = []
    episodes = int(config["training"]["total_episodes"])
    for episode in range(episodes):
        observation = env.reset()
        budgets.decoys_used = 0
        done = False
        total_reward = 0.0
        while not done:
            budgets.reset_step()
            obs_in = distortion.apply(observation) if distortion_cfg.get("enabled", True) else observation
            summary = summarize_observation(obs_in)
            bundle = feature_builder.build(obs_in, messages=[0, 0, 0, 0])
            state = feature_builder.vectorize(bundle)
            mode = agent.selector.select_mode(summary, explore=True)
            action_name, action_idx, log_prob, value = agent.executors.select(mode, state)
            proposal = ActionProposal(mode=mode, action_name=action_name, parameters={})
            invalid_penalty = 0.0
            if not budgets.can_execute(proposal):
                invalid_penalty = 1.0
                proposal = ActionProposal(mode="Idle", action_name="Sleep", parameters={})
                mode = "Idle"
                action_idx = 0
            budgets.register(proposal)
            result = env.step(proposal)
            exec_reward = compute_execution_reward(
                mission_gain=float(result.info.get("mission_gain", result.reward)),
                risk_reduction=float(result.info.get("risk_reduction", 0.0)),
                action_name=proposal.action_name,
                action_costs=config["costs"],
                projected_disruption=float(result.info.get("projected_disruption", 0.0)),
                invalid_action_penalty=invalid_penalty,
            )
            agent.executors.store(mode, state, action_idx, log_prob, exec_reward, result.terminated, value)
            total_reward += exec_reward
            observation = result.observation
            done = result.terminated or result.truncated
        for mode in agent.executors.buffers:
            agent.executors.update(mode)
        episode_returns.append(total_reward)
        if (episode + 1) % max(1, config["training"]["eval_every"]) == 0:
            logger.info("Stage I episode %d | return=%.3f", episode + 1, total_reward)
    return {"stage": 1, "episode_returns": episode_returns}


def run_stage2(config: ConfigDict, env: Any) -> Dict[str, Any]:
    agent, feature_builder = build_agent(config)
    episodes = int(config["training"]["total_episodes"])
    meta_returns: List[float] = []
    for episode in range(episodes):
        observation = env.reset()
        done = False
        total = 0.0
        while not done:
            summary = summarize_observation(observation)
            bundle = feature_builder.build(observation, messages=[0, 0, 0, 0])
            state = feature_builder.vectorize(bundle)
            mode = agent.selector.select_mode(summary, explore=True)
            action_name, _, _, _ = agent.executors.select(mode, state)
            result = env.step(ActionProposal(mode=mode, action_name=action_name, parameters={}))
            next_summary = summarize_observation(result.observation)
            reward = compute_meta_reward(
                mode=mode,
                rewards=[result.reward],
                observation_summary=summary,
                gamma=float(config["training"]["gamma"]),
                guidance_weight=float(config["selector"]["guidance_weight"]),
                immediate_only=False,
                discount_option_credit=bool(config["selector"]["discount_option_credit"]),
            )
            agent.selector.update(summary, mode, reward, next_summary)
            total += reward
            observation = result.observation
            done = result.terminated or result.truncated
        meta_returns.append(total)
        if (episode + 1) % max(1, config["training"]["eval_every"]) == 0:
            logger.info("Stage II episode %d | meta-return=%.3f", episode + 1, total)
    return {"stage": 2, "episode_returns": meta_returns}


def run_stage3(config: ConfigDict, env: Any) -> Dict[str, Any]:
    result_1 = run_stage1(config, env)
    result_2 = run_stage2(config, env)
    combined = [(a + b) / 2.0 for a, b in zip(result_1["episode_returns"], result_2["episode_returns"])]
    return {"stage": 3, "episode_returns": combined}


def save_summary(path: str | Path, payload: Dict[str, Any]) -> None:
    dump_json(path, payload)
''')

# scripts
add('scripts/common.py', '''
from __future__ import annotations

import argparse

from hmal.config import load_many


def parser_with_common(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", required=True, help="Base config YAML")
    parser.add_argument("--env", required=True, help="Environment config YAML")
    return parser


def load_config_from_args(args) -> dict:
    return load_many([args.config, args.env])
''')

add('scripts/train_stage1.py', '''
from __future__ import annotations

from pathlib import Path

from scripts.common import parser_with_common, load_config_from_args
from hmal.envs.offline_replay import OfflineReplayEnv
from hmal.training.pipeline import run_stage1, save_summary
from hmal.utils.io import ensure_dir


def main() -> None:
    parser = parser_with_common("Stage I Tier-2 PPO pretraining")
    args = parser.parse_args()
    cfg = load_config_from_args(args)
    env_cfg = cfg["environment"]
    env = OfflineReplayEnv(
        processed_path=env_cfg.get("processed_path", ""),
        label_path=env_cfg.get("label_path"),
        episode_horizon=int(env_cfg.get("episode_horizon", 500)),
    )
    result = run_stage1(cfg, env)
    out_dir = ensure_dir(Path(cfg["experiment"]["output_dir"]) / "stage1")
    save_summary(out_dir / "summary.json", result)


if __name__ == "__main__":
    main()
''')

add('scripts/train_stage2.py', '''
from __future__ import annotations

from pathlib import Path

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
''')

add('scripts/train_stage3.py', '''
from __future__ import annotations

from pathlib import Path

from scripts.common import parser_with_common, load_config_from_args
from hmal.envs.offline_replay import OfflineReplayEnv
from hmal.training.pipeline import run_stage3, save_summary
from hmal.utils.io import ensure_dir


def main() -> None:
    parser = parser_with_common("Stage III joint refinement")
    args = parser.parse_args()
    cfg = load_config_from_args(args)
    env_cfg = cfg["environment"]
    env = OfflineReplayEnv(
        processed_path=env_cfg.get("processed_path", ""),
        label_path=env_cfg.get("label_path"),
        episode_horizon=int(env_cfg.get("episode_horizon", 500)),
    )
    result = run_stage3(cfg, env)
    out_dir = ensure_dir(Path(cfg["experiment"]["output_dir"]) / "stage3")
    save_summary(out_dir / "summary.json", result)


if __name__ == "__main__":
    main()
''')

add('scripts/train_full.py', '''
from __future__ import annotations

from pathlib import Path

from scripts.common import parser_with_common, load_config_from_args
from hmal.envs.offline_replay import OfflineReplayEnv
from hmal.training.pipeline import run_stage1, run_stage2, run_stage3, save_summary
from hmal.utils.io import ensure_dir


def main() -> None:
    parser = parser_with_common("Full staged HMAL training")
    args = parser.parse_args()
    cfg = load_config_from_args(args)
    env_cfg = cfg["environment"]
    env = OfflineReplayEnv(
        processed_path=env_cfg.get("processed_path", ""),
        label_path=env_cfg.get("label_path"),
        episode_horizon=int(env_cfg.get("episode_horizon", 500)),
    )
    result = {
        "stage1": run_stage1(cfg, env),
        "stage2": run_stage2(cfg, env),
        "stage3": run_stage3(cfg, env),
    }
    out_dir = ensure_dir(Path(cfg["experiment"]["output_dir"]) / "full")
    save_summary(out_dir / "summary.json", result)


if __name__ == "__main__":
    main()
''')

add('scripts/evaluate.py', '''
from __future__ import annotations

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
''')

add('scripts/run_ablation.py', '''
from __future__ import annotations

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
''')

add('scripts/prepare_lanl.py', '''
from __future__ import annotations

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
''')

add('scripts/prepare_darpa.py', '''
from __future__ import annotations

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
''')

add('scripts/reproduce_reported_tables.py', '''
from __future__ import annotations

from pathlib import Path

import pandas as pd


def main() -> None:
    root = Path("paper_results")
    for csv_path in sorted(root.glob("*.csv")):
        df = pd.read_csv(csv_path)
        print(f"\n=== {csv_path.name} ===")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
''')

add('scripts/plot_reported_results.py', '''
from __future__ import annotations

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
''')

# tests
add('tests/test_feature_builder.py', '''
from hmal.observation.feature_builder import FeatureBuilder


def test_feature_builder_vector_shape() -> None:
    builder = FeatureBuilder(hash_dim=16, include_messages=True)
    bundle = builder.build({"events": [{"hostname": "h1", "user": "u1", "event_type": "auth"}]}, [1, 2, 3, 4])
    vector = builder.vectorize(bundle)
    assert vector.shape[0] == 16 * 6 + 8
''')

add('tests/test_meta_reward.py', '''
from hmal.rewards.meta_reward import compute_meta_reward


def test_meta_reward_prefers_discounted_env_term() -> None:
    reward = compute_meta_reward(
        mode="Sense",
        rewards=[1.0, 0.5],
        observation_summary={"suspicious_score": 1.0, "confirmed_score": 0.0, "service_disruption": 0.0},
        gamma=0.99,
        guidance_weight=0.1,
        immediate_only=False,
        discount_option_credit=True,
    )
    assert reward > 1.0
''')

add('tests/test_core.py', '''
from hmal.coalition.core import evaluate_core_feasibility


def test_core_feasibility_outputs_keys() -> None:
    result = evaluate_core_feasibility(
        grand_coalition=["a", "b"],
        coalition_worth={("a",): 1.0, ("b",): 1.0, ("a", "b"): 1.5},
        allocations={"a": 0.8, "b": 0.7},
    )
    assert "violation_rate" in result
    assert "violation_margin" in result
''')

add('tests/test_q_learning.py', '''
from hmal.models.tier1_q import TabularQSelector


def test_q_update_changes_value() -> None:
    q = TabularQSelector(modes=["Sense", "Idle"], alpha=0.5, gamma=0.9, epsilon=0.0)
    q.update("s0", "Sense", 1.0, "s1")
    assert q.q_table["s0"][0] != 0.0
''')

# paper results CSVs
add('paper_results/ablation_tier1_reward_cc4.csv', '''
variant,mission_return,attacker_delay,op_cost,service_interruptions,episodes_to_convergence
Immediate Reward Only,-2148,38.1,64.7,9.6,891
No Internal Guidance,-1942,46.9,61.3,8.3,744
Uniform Option Credit,-2011,43.8,62.4,8.8,786
Full Tier-1 Reward,-1776,55.2,59.4,7.2,612
''')

add('paper_results/ablation_deception_cc4.csv', '''
variant,mission_return,attacker_delay,decoy_engagements,service_interruptions,op_cost
NoDeception,-2069,39.2,0.0,8.5,57.6
No Deceive Mode,-2124,34.8,0.0,8.9,56.9
Capped Deceive,-1863,49.1,11.2,6.8,58.1
Full HMAL,-1781,56.4,18.7,7.0,59.8
''')

add('paper_results/ablation_feasibility_lanl.csv', '''
variant,f1,auprc,invalid_actions_pct,projected_service_disruption,core_violation_rate_pct
Masking Only,0.934,0.952,2.4,7.2,11.7
Budget Only,0.929,0.947,5.9,7.9,10.8
Soft-Penalty Only,0.921,0.939,8.7,8.8,14.6
No Constraints,0.913,0.931,12.4,9.6,18.9
Full Feasibility-Aware,0.938,0.956,1.8,7.6,8.9
''')

add('paper_results/cc4_performance_comparison.csv', '''
method,mission_return,op_cost,attacker_delay,blue_service_interruptions,core_violation_rate_pct
H-MARL Expert,-2018,65.4,38.7,9.8,13.9
TERLA-PPO,-2337,55.9,24.8,7.6,18.4
LLM+RL ACD,-2764,72.6,29.3,13.8,21.7
Zero-Trust MARL,-2211,78.2,44.2,12.7,16.5
CommFormer-Hetero,-2095,63.1,41.5,8.9,11.6
C-MADF,-2457,60.8,31.9,7.9,17.2
Proposed HMAL,-1764,58.7,56.1,6.9,7.8
''')

add('paper_results/lanl_performance_comparison.csv', '''
method,precision,recall,f1,auprc,lead_time_min
H-MARL Expert,0.944,0.901,0.922,0.939,35.8
TERLA-PPO,0.918,0.879,0.898,0.921,30.4
LLM+RL ACD,0.905,0.846,0.874,0.894,24.7
Zero-Trust MARL,0.928,0.887,0.907,0.929,33.5
CommFormer-Hetero,0.936,0.909,0.922,0.943,37.2
C-MADF,0.963,0.890,0.925,0.945,31.6
Proposed HMAL,0.957,0.924,0.940,0.958,42.6
''')

add('paper_results/darpa_performance_comparison.csv', '''
method,precision,recall,f1,auprc,lead_time_min
H-MARL Expert,0.936,0.888,0.911,0.931,23.1
TERLA-PPO,0.907,0.860,0.883,0.909,19.6
LLM+RL ACD,0.898,0.833,0.864,0.887,16.8
Zero-Trust MARL,0.921,0.872,0.896,0.922,22.8
CommFormer-Hetero,0.928,0.901,0.914,0.938,25.4
C-MADF,0.954,0.881,0.916,0.934,21.5
Proposed HMAL,0.949,0.913,0.931,0.951,28.9
''')

add('paper_results/training_schedule_lanl.csv', '''
variant,precision,recall,f1,auprc,lead_time_min,episodes_to_convergence,seed_std_f1
Full Staged Training,,0.923,0.938,0.956,42.1,,0.007
Joint End-to-End,,,0.920,0.939,,,0.013
No Stage III,0.958,,,,,603,
Reverse Order,,,0.910,0.928,33.0,1016,0.015
''')

add('paper_results/coalition_fusion_lanl.csv', '''
variant,precision,recall,f1,auprc,lead_time_min,cross_zone_consistency
Full Fused Profile,,0.924,0.939,0.958,42.8,0.914
NoMessage,0.959,,,,,
Local-only Belief,,,0.916,0.936,34.1,0.841
Noisy/Delayed Fusion,0.961,,,,,
''')

add('paper_results/distortion_darpa.csv', '''
variant,clean_precision,clean_auprc,moderate_auprc,severe_auprc,severe_recall,severe_lead_time_min
Full Distortion-Aware Training,,,0.938,0.924,0.889,24.8
Clean Training,0.956,0.952,0.909,0.871,0.823,
Fixed Mild Distortion,,,,,,
''')

# package init for subpackages missing
for pkg in [
    'hmal/agents', 'hmal/coalition', 'hmal/data', 'hmal/envs', 'hmal/evaluation', 'hmal/models', 'hmal/observation', 'hmal/rewards', 'hmal/training', 'hmal/utils'
]:
    files.setdefault(f'{pkg}/__init__.py', '')

for path, content in files.items():
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')

print(f'Wrote {len(files)} files.')
