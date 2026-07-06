import json
from decimal import Decimal
from pathlib import Path

from market_micstr_lab.data.jsonl import read_jsonl
from market_micstr_lab.research.baseline import (
    DEFAULT_THRESHOLDS,
    evaluate_imbalance_rule,
)


def usable_labeled_rows(rows: list[dict], depth: int, horizon: int) -> list[dict]:
    feature_key = f"imbalance_{depth}"
    label_key = f"mid_price_direction_{horizon}"

    return [
        row
        for row in rows
        if row.get(feature_key) is not None and row.get(label_key) is not None
    ]


def walk_forward_windows(
    rows: list[dict],
    train_size: int,
    test_size: int,
    step_size: int,
) -> list[dict]:
    if train_size <= 0:
        raise ValueError("train_size must be positive")
    if test_size <= 0:
        raise ValueError("test_size must be positive")
    if step_size <= 0:
        raise ValueError("step_size must be positive")

    windows = []
    start = 0

    while start + train_size + test_size <= len(rows):
        train_start = start
        train_end = train_start + train_size
        test_start = train_end
        test_end = test_start + test_size

        windows.append(
            {
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
            }
        )

        start += step_size

    return windows


def _best_threshold_result(
    train_rows: list[dict],
    depth: int,
    horizon: int,
    thresholds: list[Decimal],
) -> tuple[Decimal, dict, list[dict]]:
    threshold_results = [
        evaluate_imbalance_rule(
            train_rows,
            depth=depth,
            horizon=horizon,
            threshold=threshold,
        )
        for threshold in thresholds
    ]

    best_index = 0
    best_accuracy = Decimal("-1")

    for index, result in enumerate(threshold_results):
        accuracy = result["accuracy"]
        score = Decimal(str(accuracy)) if accuracy is not None else Decimal("-1")

        if score > best_accuracy:
            best_accuracy = score
            best_index = index

    return thresholds[best_index], threshold_results[best_index], threshold_results


def _accuracy_values(window_results: list[dict]) -> list[float]:
    values = []

    for result in window_results:
        accuracy = result["test"]["accuracy"]
        if accuracy is not None:
            values.append(float(accuracy))

    return values


def run_walk_forward_imbalance_baseline(
    rows: list[dict],
    depth: int = 1,
    horizon: int = 1,
    train_size: int = 1000,
    test_size: int = 200,
    step_size: int = 200,
    thresholds: list[Decimal] | None = None,
) -> dict:
    candidate_thresholds = thresholds or DEFAULT_THRESHOLDS
    usable_rows = usable_labeled_rows(rows, depth=depth, horizon=horizon)
    windows = walk_forward_windows(
        usable_rows,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
    )

    window_results = []

    for index, window in enumerate(windows):
        train_rows = usable_rows[window["train_start"] : window["train_end"]]
        test_rows = usable_rows[window["test_start"] : window["test_end"]]

        best_threshold, train_result, threshold_search = _best_threshold_result(
            train_rows,
            depth=depth,
            horizon=horizon,
            thresholds=candidate_thresholds,
        )

        test_result = evaluate_imbalance_rule(
            test_rows,
            depth=depth,
            horizon=horizon,
            threshold=best_threshold,
        )

        window_results.append(
            {
                "window": index,
                "train_start": window["train_start"],
                "train_end": window["train_end"],
                "test_start": window["test_start"],
                "test_end": window["test_end"],
                "best_threshold": str(best_threshold),
                "train": train_result,
                "test": test_result,
                "threshold_search": threshold_search,
            }
        )

    accuracies = _accuracy_values(window_results)

    return {
        "model": "walk_forward_imbalance_threshold",
        "feature": f"imbalance_{depth}",
        "label": f"mid_price_direction_{horizon}",
        "input_rows": len(rows),
        "usable_rows": len(usable_rows),
        "train_size": train_size,
        "test_size": test_size,
        "step_size": step_size,
        "candidate_thresholds": [str(threshold) for threshold in candidate_thresholds],
        "window_count": len(window_results),
        "mean_test_accuracy": sum(accuracies) / len(accuracies) if accuracies else None,
        "min_test_accuracy": min(accuracies) if accuracies else None,
        "max_test_accuracy": max(accuracies) if accuracies else None,
        "windows": window_results,
    }


def write_walk_forward_report_json(
    input_path: str | Path,
    output_path: str | Path,
    depth: int = 1,
    horizon: int = 1,
    train_size: int = 1000,
    test_size: int = 200,
    step_size: int = 200,
    thresholds: list[Decimal] | None = None,
) -> dict:
    report = run_walk_forward_imbalance_baseline(
        list(read_jsonl(input_path)),
        depth=depth,
        horizon=horizon,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
        thresholds=thresholds,
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, sort_keys=True)
        file.write("\n")

    return report
