import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from market_micstr_lab.data.jsonl import read_jsonl


DEFAULT_THRESHOLDS = [
    Decimal("0"),
    Decimal("0.05"),
    Decimal("0.10"),
    Decimal("0.20"),
    Decimal("0.30"),
    Decimal("0.50"),
]
DIRECTIONS = [-1, 0, 1]


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _to_direction(value: Any) -> int | None:
    if value is None:
        return None
    direction = int(value)
    if direction not in DIRECTIONS:
        raise ValueError(f"Unsupported direction: {value}")
    return direction


def parse_thresholds(text: str) -> list[Decimal]:
    thresholds = [Decimal(item.strip()) for item in text.split(",") if item.strip()]
    if not thresholds:
        raise ValueError("at least one threshold is required")
    if any(threshold < 0 for threshold in thresholds):
        raise ValueError("thresholds must be non-negative")
    return thresholds


def predict_from_imbalance(imbalance: Any, threshold: Decimal = Decimal("0")) -> int:
    value = _to_decimal(imbalance)
    if value is None:
        raise ValueError("imbalance is required")

    if value > threshold:
        return 1
    if value < -threshold:
        return -1
    return 0


def _usable_rows(rows: list[dict], depth: int, horizon: int) -> list[dict]:
    feature_key = f"imbalance_{depth}"
    label_key = f"mid_price_direction_{horizon}"

    return [
        row
        for row in rows
        if row.get(feature_key) is not None and row.get(label_key) is not None
    ]


def split_chronologically(rows: list[dict], train_fraction: float = 0.7) -> tuple[list[dict], list[dict]]:
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")

    if len(rows) < 2:
        return rows, []

    split_index = int(len(rows) * train_fraction)
    split_index = max(1, min(len(rows) - 1, split_index))
    return rows[:split_index], rows[split_index:]


def evaluate_imbalance_rule(
    rows: list[dict],
    depth: int = 1,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
) -> dict:
    feature_key = f"imbalance_{depth}"
    label_key = f"mid_price_direction_{horizon}"
    prediction_counts = {str(direction): 0 for direction in DIRECTIONS}
    label_counts = {str(direction): 0 for direction in DIRECTIONS}
    confusion_matrix = {
        str(label): {str(prediction): 0 for prediction in DIRECTIONS}
        for label in DIRECTIONS
    }
    correct = 0
    evaluated = 0

    for row in rows:
        label = _to_direction(row.get(label_key))
        if label is None:
            continue

        prediction = predict_from_imbalance(row.get(feature_key), threshold=threshold)
        evaluated += 1
        if prediction == label:
            correct += 1

        prediction_counts[str(prediction)] += 1
        label_counts[str(label)] += 1
        confusion_matrix[str(label)][str(prediction)] += 1

    accuracy = correct / evaluated if evaluated else None

    return {
        "threshold": str(threshold),
        "evaluated_rows": evaluated,
        "correct": correct,
        "accuracy": accuracy,
        "prediction_counts": prediction_counts,
        "label_counts": label_counts,
        "confusion_matrix": confusion_matrix,
    }


def run_imbalance_baseline(
    rows: list[dict],
    depth: int = 1,
    horizon: int = 1,
    train_fraction: float = 0.7,
    thresholds: list[Decimal] | None = None,
) -> dict:
    candidate_thresholds = thresholds or DEFAULT_THRESHOLDS
    usable_rows = _usable_rows(rows, depth=depth, horizon=horizon)
    train_rows, test_rows = split_chronologically(usable_rows, train_fraction=train_fraction)

    train_results = [
        evaluate_imbalance_rule(
            train_rows,
            depth=depth,
            horizon=horizon,
            threshold=threshold,
        )
        for threshold in candidate_thresholds
    ]

    best_index = 0
    best_accuracy = Decimal("-1")
    for index, result in enumerate(train_results):
        accuracy = result["accuracy"]
        score = Decimal(str(accuracy)) if accuracy is not None else Decimal("-1")
        if score > best_accuracy:
            best_accuracy = score
            best_index = index

    best_threshold = candidate_thresholds[best_index]

    return {
        "model": "imbalance_threshold",
        "feature": f"imbalance_{depth}",
        "label": f"mid_price_direction_{horizon}",
        "input_rows": len(rows),
        "usable_rows": len(usable_rows),
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "train_fraction": train_fraction,
        "candidate_thresholds": [str(threshold) for threshold in candidate_thresholds],
        "best_threshold": str(best_threshold),
        "train": train_results[best_index],
        "test": evaluate_imbalance_rule(
            test_rows,
            depth=depth,
            horizon=horizon,
            threshold=best_threshold,
        ),
        "threshold_search": train_results,
    }


def write_imbalance_baseline_report_json(
    input_path: str | Path,
    output_path: str | Path,
    depth: int = 1,
    horizon: int = 1,
    train_fraction: float = 0.7,
    thresholds: list[Decimal] | None = None,
) -> dict:
    report = run_imbalance_baseline(
        list(read_jsonl(input_path)),
        depth=depth,
        horizon=horizon,
        train_fraction=train_fraction,
        thresholds=thresholds,
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, sort_keys=True)
        file.write("\n")

    return report
