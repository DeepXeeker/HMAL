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
