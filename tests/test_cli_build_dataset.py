import subprocess
import sys

from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl


def test_cli_build_dataset(tmp_path) -> None:
    input_path = tmp_path / "book_events.jsonl"
    output_path = tmp_path / "dataset.jsonl"

    write_jsonl(
        input_path,
        [
            {
                "channel": "book",
                "event_type": "snapshot",
                "recv_seq": 1,
                "symbol": "BTC/USD",
                "bids": [["100.00", "3.0"]],
                "asks": [["100.50", "1.0"]],
            },
            {
                "channel": "book",
                "event_type": "update",
                "recv_seq": 2,
                "symbol": "BTC/USD",
                "bids": [["100.50", "3.0"]],
                "asks": [["100.50", "0"], ["101.00", "1.0"]],
            },
        ],
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "market_micstr_lab.cli.build_dataset",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--depth",
            "1",
            "--horizon",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = list(read_jsonl(output_path))

    assert "Wrote 2 labeled feature rows" in result.stdout
    assert len(rows) == 2
    assert rows[0]["mid_price"] == "100.25"
    assert rows[0]["future_mid_price_1"] == "100.75"
    assert rows[0]["mid_price_direction_1"] == 1


def test_cli_build_dataset_help_includes_checksum_validation() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "market_micstr_lab.cli.build_dataset", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "--validate-checksum" in result.stdout
    assert "--checksum-depth" in result.stdout
