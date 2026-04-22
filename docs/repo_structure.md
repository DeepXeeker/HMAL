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
