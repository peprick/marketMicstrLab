import json
import subprocess
import sys
from decimal import Decimal

import pytest

from market_micstr_lab.data.jsonl import write_jsonl
from market_micstr_lab.research.baseline import (
    evaluate_imbalance_rule,
    parse_thresholds,
    predict_from_imbalance,
    run_imbalance_baseline,
    split_chronologically,
    write_imbalance_baseline_report_json,
)


def labeled_rows() -> list[dict]:
    return [
        {
            "imbalance_1": "0.80",
            "mid_price_direction_1": 1,
        },
        {
            "imbalance_1": "-0.70",
            "mid_price_direction_1": -1,
        },
        {
            "imbalance_1": "0.10",
            "mid_price_direction_1": 0,
        },
        {
            "imbalance_1": "0.90",
            "mid_price_direction_1": None,
        },
    ]


def test_parse_thresholds() -> None:
    assert parse_thresholds("0, 0.05,0.2") == [
        Decimal("0"),
        Decimal("0.05"),
        Decimal("0.2"),
    ]

    with pytest.raises(ValueError, match="non-negative"):
        parse_thresholds("-0.1")


def test_predict_from_imbalance() -> None:
    assert predict_from_imbalance("0.30", threshold=Decimal("0.20")) == 1
    assert predict_from_imbalance("-0.30", threshold=Decimal("0.20")) == -1
    assert predict_from_imbalance("0.10", threshold=Decimal("0.20")) == 0


def test_evaluate_imbalance_rule() -> None:
    result = evaluate_imbalance_rule(
        labeled_rows(),
        depth=1,
        horizon=1,
        threshold=Decimal("0.20"),
    )

    assert result["evaluated_rows"] == 3
    assert result["correct"] == 3
    assert result["accuracy"] == 1.0
    assert result["prediction_counts"] == {"-1": 1, "0": 1, "1": 1}


def test_split_chronologically_keeps_order_and_test_rows() -> None:
    rows = [{"row": index} for index in range(5)]

    train, test = split_chronologically(rows, train_fraction=0.6)

    assert train == [{"row": 0}, {"row": 1}, {"row": 2}]
    assert test == [{"row": 3}, {"row": 4}]


def test_run_imbalance_baseline_selects_best_train_threshold() -> None:
    report = run_imbalance_baseline(
        labeled_rows(),
        depth=1,
        horizon=1,
        train_fraction=0.67,
        thresholds=[Decimal("0"), Decimal("0.20")],
    )

    assert report["model"] == "imbalance_threshold"
    assert report["feature"] == "imbalance_1"
    assert report["label"] == "mid_price_direction_1"
    assert report["usable_rows"] == 3
    assert report["best_threshold"] == "0"
    assert report["test"]["evaluated_rows"] == 1


def test_write_imbalance_baseline_report_json(tmp_path) -> None:
    input_path = tmp_path / "dataset.jsonl"
    output_path = tmp_path / "baseline.json"
    write_jsonl(input_path, labeled_rows())

    report = write_imbalance_baseline_report_json(
        input_path=input_path,
        output_path=output_path,
        depth=1,
        horizon=1,
        train_fraction=0.67,
        thresholds=[Decimal("0"), Decimal("0.20")],
    )

    with output_path.open("r", encoding="utf-8") as file:
        saved = json.load(file)

    assert saved == report
    assert saved["best_threshold"] == "0"


def test_run_baseline_cli(tmp_path) -> None:
    input_path = tmp_path / "dataset.jsonl"
    output_path = tmp_path / "baseline.json"
    write_jsonl(input_path, labeled_rows())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "market_micstr_lab.cli.run_baseline",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--depth",
            "1",
            "--horizon",
            "1",
            "--train-fraction",
            "0.67",
            "--thresholds",
            "0,0.20",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    with output_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert "Wrote imbalance baseline report" in result.stdout
    assert report["best_threshold"] == "0"
