import asyncio
import subprocess
import sys

from market_micstr_lab.cli.capture_dataset import capture_dataset
from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl


async def fake_capture_messages(
    output_path,
    channel: str,
    symbol: str,
    depth: int,
    snapshot: bool,
    max_messages: int | None,
    seconds: float | None,
) -> int:
    assert channel == "book"
    assert symbol == "BTC/USD"
    assert depth == 10
    assert snapshot is True
    assert max_messages == 2
    assert seconds is None

    write_jsonl(
        output_path,
        [
            {
                "source": "kraken_ws_v2",
                "depth": depth,
                "capture_ts_ns": 1780000000000000000,
                "recv_seq": 1,
                "payload": {
                    "channel": "book",
                    "type": "snapshot",
                    "data": [
                        {
                            "symbol": symbol,
                            "timestamp": "2026-07-03T10:00:00.000000Z",
                            "bids": [{"price": "100.00", "qty": "3.0"}],
                            "asks": [{"price": "100.50", "qty": "1.0"}],
                            "checksum": 1,
                        }
                    ],
                },
            },
            {
                "source": "kraken_ws_v2",
                "depth": depth,
                "capture_ts_ns": 1780000000000000001,
                "recv_seq": 2,
                "payload": {
                    "channel": "book",
                    "type": "update",
                    "data": [
                        {
                            "symbol": symbol,
                            "timestamp": "2026-07-03T10:00:01.000000Z",
                            "bids": [{"price": "100.50", "qty": "3.0"}],
                            "asks": [
                                {"price": "100.50", "qty": "0"},
                                {"price": "101.00", "qty": "1.0"},
                            ],
                            "checksum": 2,
                        }
                    ],
                },
            },
        ],
    )

    return 2


def test_capture_dataset_runs_full_pipeline_with_fake_capture(tmp_path) -> None:
    raw_output = tmp_path / "raw.jsonl"
    events_output = tmp_path / "events.jsonl"
    dataset_output = tmp_path / "dataset.jsonl"

    counts = asyncio.run(
        capture_dataset(
            raw_output=raw_output,
            events_output=events_output,
            dataset_output=dataset_output,
            symbol="BTC/USD",
            capture_depth=10,
            feature_depth=1,
            max_messages=2,
            horizon=1,
            validate=True,
            capture_func=fake_capture_messages,
        )
    )

    events = list(read_jsonl(events_output))
    rows = list(read_jsonl(dataset_output))

    assert counts == {"raw": 2, "events": 2, "dataset": 2}
    assert events[0]["event_type"] == "snapshot"
    assert events[1]["event_type"] == "update"
    assert rows[0]["mid_price"] == "100.25"
    assert rows[0]["future_mid_price_1"] == "100.75"
    assert rows[0]["mid_price_direction_1"] == 1


def test_capture_dataset_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "market_micstr_lab.cli.capture_dataset", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Capture Kraken book data, normalize it, and build labeled features." in result.stdout
    assert "--feature-depth" in result.stdout
    assert "--validate-checksum" in result.stdout
    assert "--checksum-depth" in result.stdout
