import json
import subprocess
import sys
from decimal import Decimal

import pytest

from market_micstr_lab.data.jsonl import write_jsonl
from market_micstr_lab.research.execution import (
    execution_cost,
    run_execution_simulation,
    simulate_row_execution,
    summarize_execution,
    write_execution_report_json,
)


def sample_rows() -> list[dict]:
    return [
        {
            "recv_seq": 1,
            "mid_price": "100.00",
            "spread": "0.10",
            "imbalance_1": "0.80",
            "mid_price_delta_1": "0.50",
        },
        {
            "recv_seq": 2,
            "mid_price": "100.50",
            "spread": "0.10",
            "imbalance_1": "-0.70",
            "mid_price_delta_1": "-0.25",
        },
        {
            "recv_seq": 3,
            "mid_price": "100.25",
            "spread": "0.10",
            "imbalance_1": "0.05",
            "mid_price_delta_1": "0.00",
        },
    ]


def test_execution_cost_includes_spread_fee_and_slippage() -> None:
    cost = execution_cost(
        mid_price="100",
        spread="0.10",
        fee_bps=Decimal("1"),
        slippage_bps=Decimal("2"),
    )

    assert cost == Decimal("0.160")


def test_execution_cost_rejects_negative_cost_inputs() -> None:
    with pytest.raises(ValueError, match="fee_bps"):
        execution_cost("100", "0.10", fee_bps=Decimal("-1"))

    with pytest.raises(ValueError, match="slippage_bps"):
        execution_cost("100", "0.10", slippage_bps=Decimal("-1"))


def test_simulate_row_execution_long_signal() -> None:
    result = simulate_row_execution(
        sample_rows()[0],
        depth=1,
        horizon=1,
        threshold=Decimal("0.20"),
        fee_bps=Decimal("0"),
        slippage_bps=Decimal("0"),
    )

    assert result == {
        "recv_seq": 1,
        "signal": 1,
        "gross_pnl": "0.50",
        "cost": "0.10",
        "net_pnl": "0.40",
    }


def test_simulate_row_execution_short_signal() -> None:
    result = simulate_row_execution(
        sample_rows()[1],
        depth=1,
        horizon=1,
        threshold=Decimal("0.20"),
        fee_bps=Decimal("0"),
        slippage_bps=Decimal("0"),
    )

    assert result["signal"] == -1
    assert result["gross_pnl"] == "0.25"
    assert result["net_pnl"] == "0.15"


def test_summarize_execution() -> None:
    report = run_execution_simulation(
        sample_rows(),
        depth=1,
        horizon=1,
        threshold=Decimal("0.20"),
    )

    summary = report["summary"]

    assert summary["evaluated_rows"] == 3
    assert summary["trade_count"] == 2
    assert summary["win_rate"] == 1.0
    assert summary["total_gross_pnl"] == "0.75"
    assert summary["total_cost"] == "0.20"
    assert summary["total_net_pnl"] == "0.55"


def test_write_execution_report_json(tmp_path) -> None:
    input_path = tmp_path / "dataset.jsonl"
    output_path = tmp_path / "execution.json"
    write_jsonl(input_path, sample_rows())

    report = write_execution_report_json(
        input_path=input_path,
        output_path=output_path,
        depth=1,
        horizon=1,
        threshold=Decimal("0.20"),
    )

    with output_path.open("r", encoding="utf-8") as file:
        saved = json.load(file)

    assert saved == report
    assert saved["summary"]["trade_count"] == 2


def test_run_execution_cli(tmp_path) -> None:
    input_path = tmp_path / "dataset.jsonl"
    output_path = tmp_path / "execution.json"
    write_jsonl(input_path, sample_rows())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "market_micstr_lab.cli.run_execution",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--depth",
            "1",
            "--horizon",
            "1",
            "--threshold",
            "0.20",
            "--fee-bps",
            "0",
            "--slippage-bps",
            "0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    with output_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert "Wrote execution report" in result.stdout
    assert report["summary"]["trade_count"] == 2
