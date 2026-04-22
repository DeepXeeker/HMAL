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
