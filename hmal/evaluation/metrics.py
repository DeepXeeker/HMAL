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
