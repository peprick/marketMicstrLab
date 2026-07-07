import json
import subprocess
import sys

from market_micstr_lab.research.report_site import build_report_site


def _write_json(path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_report_site_writes_dashboard(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    figures_dir = reports_dir / "figures"
    figures_dir.mkdir(parents=True)

    _write_json(
        reports_dir / "baseline_imbalance.json",
        {
            "model": "imbalance_threshold",
            "feature": "imbalance_1",
            "label": "mid_price_direction_1",
            "usable_rows": 10,
            "test_rows": 3,
            "best_threshold": "0.10",
            "test": {"accuracy": 0.5},
            "threshold_search": [
                {"threshold": "0.10", "evaluated_rows": 7, "correct": 4, "accuracy": 0.5}
            ],
        },
    )
    _write_json(
        reports_dir / "walk_forward_imbalance.json",
        {
            "model": "walk_forward_imbalance_threshold",
            "feature": "imbalance_1",
            "label": "mid_price_direction_1",
            "window_count": 1,
            "mean_test_accuracy": 0.5,
            "min_test_accuracy": 0.25,
            "max_test_accuracy": 0.75,
            "windows": [
                {
                    "window": 0,
                    "best_threshold": "0.10",
                    "test": {"evaluated_rows": 4, "correct": 2, "accuracy": 0.5},
                }
            ],
        },
    )
    _write_json(
        reports_dir / "execution_imbalance.json",
        {
            "model": "imbalance_threshold_execution",
            "feature": "imbalance_1",
            "horizon": 1,
            "threshold": "0.10",
            "fee_bps": "1",
            "slippage_bps": "2",
            "latency_events": 1,
            "queue_fill_fraction": "0.50",
            "summary": {
                "trade_count": 2,
                "win_rate": 0.5,
                "total_net_pnl": "0.25",
            },
        },
    )
    (figures_dir / "mid_price.svg").write_text(
        '<svg viewBox="0 0 10 10"><path d="M0 5L10 5"/></svg>',
        encoding="utf-8",
    )

    output_path = build_report_site(reports_dir)

    html = output_path.read_text(encoding="utf-8")
    assert "Market Microstructure Lab Viewer" in html
    assert "Baseline Accuracy" in html
    assert "Walk Forward" in html
    assert "Execution Assumptions" in html
    assert "Mid Price" in html


def test_build_report_site_cli(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    output_path = tmp_path / "site" / "index.html"
    reports_dir.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "market_micstr_lab.cli.build_report_site",
            "--reports-dir",
            str(reports_dir),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Wrote report site" in result.stdout
    assert output_path.exists()
    assert "Market Microstructure Lab Viewer" in output_path.read_text(encoding="utf-8")
