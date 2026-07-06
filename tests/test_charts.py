import json
import subprocess
import sys

from market_micstr_lab.data.jsonl import write_jsonl
from market_micstr_lab.research.charts import (
    series_from_rows,
    write_research_charts,
)


def test_series_from_rows_skips_none_values() -> None:
    rows = [
        {"mid_price": "100.25"},
        {"mid_price": None},
        {"mid_price": "100.75"},
    ]

    assert series_from_rows(rows, "mid_price") == [100.25, 100.75]


def test_write_research_charts(tmp_path) -> None:
    dataset_path = tmp_path / "dataset.jsonl"
    baseline_path = tmp_path / "baseline.json"
    output_dir = tmp_path / "figures"

    write_jsonl(
        dataset_path,
        [
            {
                "mid_price": "100.25",
                "spread": "0.50",
                "imbalance_1": "0.50",
            },
            {
                "mid_price": "100.75",
                "spread": "0.25",
                "imbalance_1": "-0.25",
            },
        ],
    )

    baseline_path.write_text(
        json.dumps(
            {
                "train": {"accuracy": 0.75},
                "test": {"accuracy": 0.50},
            }
        ),
        encoding="utf-8",
    )

    paths = write_research_charts(
        dataset_path=dataset_path,
        baseline_path=baseline_path,
        output_dir=output_dir,
        imbalance_depth=1,
    )

    assert set(paths) == {"mid_price", "spread", "imbalance", "baseline_accuracy"}

    for path in paths.values():
        content = open(path, "r", encoding="utf-8").read()
        assert content.startswith("<svg")
        assert "</svg>" in content


def test_plot_research_cli(tmp_path) -> None:
    dataset_path = tmp_path / "dataset.jsonl"
    baseline_path = tmp_path / "baseline.json"
    output_dir = tmp_path / "figures"

    write_jsonl(
        dataset_path,
        [
            {
                "mid_price": "100.25",
                "spread": "0.50",
                "imbalance_1": "0.50",
            },
            {
                "mid_price": "100.75",
                "spread": "0.25",
                "imbalance_1": "-0.25",
            },
        ],
    )

    baseline_path.write_text(
        json.dumps(
            {
                "train": {"accuracy": 0.75},
                "test": {"accuracy": 0.50},
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "market_micstr_lab.cli.plot_research",
            "--dataset",
            str(dataset_path),
            "--baseline",
            str(baseline_path),
            "--output-dir",
            str(output_dir),
            "--imbalance-depth",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Wrote mid_price chart" in result.stdout
    assert (output_dir / "mid_price.svg").exists()
    assert (output_dir / "spread.svg").exists()
    assert (output_dir / "imbalance_1.svg").exists()
    assert (output_dir / "baseline_accuracy.svg").exists()
