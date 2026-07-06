import json
import subprocess
import sys
from decimal import Decimal

import pytest

from market_micstr_lab.data.jsonl import write_jsonl
from market_micstr_lab.research.walk_forward import (
    run_walk_forward_imbalance_baseline,
    usable_labeled_rows,
    walk_forward_windows,
    write_walk_forward_report_json,
)


def sample_rows() -> list[dict]:
    return [
        {"imbalance_1": "0.80", "mid_price_direction_1": 1},
        {"imbalance_1": "-0.70", "mid_price_direction_1": -1},
        {"imbalance_1": "0.05", "mid_price_direction_1": 0},
        {"imbalance_1": "0.60", "mid_price_direction_1": 1},
        {"imbalance_1": "-0.80", "mid_price_direction_1": -1},
        {"imbalance_1": "0.00", "mid_price_direction_1": 0},
        {"imbalance_1": "0.90", "mid_price_direction_1": 1},
        {"imbalance_1": "-0.40", "mid_price_direction_1": -1},
    ]


def test_usable_labeled_rows_filters_missing_feature_or_label() -> None:
    rows = [
        {"imbalance_1": "0.5", "mid_price_direction_1": 1},
        {"imbalance_1": None, "mid_price_direction_1": 1},
        {"imbalance_1": "0.2", "mid_price_direction_1": None},
    ]

    assert usable_labeled_rows(rows, depth=1, horizon=1) == [
        {"imbalance_1": "0.5", "mid_price_direction_1": 1}
    ]


def test_walk_forward_windows_keeps_chronological_boundaries() -> None:
    rows = [{"row": index} for index in range(6)]

    windows = walk_forward_windows(
        rows,
        train_size=3,
        test_size=2,
        step_size=1,
    )

    assert windows == [
        {"train_start": 0, "train_end": 3, "test_start": 3, "test_end": 5},
        {"train_start": 1, "train_end": 4, "test_start": 4, "test_end": 6},
    ]


def test_walk_forward_windows_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError, match="train_size"):
        walk_forward_windows([], train_size=0, test_size=1, step_size=1)

    with pytest.raises(ValueError, match="test_size"):
        walk_forward_windows([], train_size=1, test_size=0, step_size=1)

    with pytest.raises(ValueError, match="step_size"):
        walk_forward_windows([], train_size=1, test_size=1, step_size=0)


def test_run_walk_forward_imbalance_baseline() -> None:
    report = run_walk_forward_imbalance_baseline(
        sample_rows(),
        depth=1,
        horizon=1,
        train_size=3,
        test_size=2,
        step_size=2,
        thresholds=[Decimal("0"), Decimal("0.20")],
    )

    assert report["model"] == "walk_forward_imbalance_threshold"
    assert report["feature"] == "imbalance_1"
    assert report["label"] == "mid_price_direction_1"
    assert report["usable_rows"] == 8
    assert report["window_count"] == 2
    assert report["mean_test_accuracy"] is not None
    assert report["windows"][0]["test"]["evaluated_rows"] == 2


def test_write_walk_forward_report_json(tmp_path) -> None:
    input_path = tmp_path / "dataset.jsonl"
    output_path = tmp_path / "walk_forward.json"
    write_jsonl(input_path, sample_rows())

    report = write_walk_forward_report_json(
        input_path=input_path,
        output_path=output_path,
        depth=1,
        horizon=1,
        train_size=3,
        test_size=2,
        step_size=2,
        thresholds=[Decimal("0"), Decimal("0.20")],
    )

    with output_path.open("r", encoding="utf-8") as file:
        saved = json.load(file)

    assert saved == report
    assert saved["window_count"] == 2


def test_run_walk_forward_cli(tmp_path) -> None:
    input_path = tmp_path / "dataset.jsonl"
    output_path = tmp_path / "walk_forward.json"
    write_jsonl(input_path, sample_rows())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "market_micstr_lab.cli.run_walk_forward",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--depth",
            "1",
            "--horizon",
            "1",
            "--train-size",
            "3",
            "--test-size",
            "2",
            "--step-size",
            "2",
            "--thresholds",
            "0,0.20",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    with output_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert "Wrote walk-forward report" in result.stdout
    assert report["window_count"] == 2
