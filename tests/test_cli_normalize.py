
import subprocess
import sys

from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl


def test_cli_normalizes_book_jsonl(tmp_path) -> None:
    input_path = tmp_path / "raw_book.jsonl"
    output_path = tmp_path / "processed_book.jsonl"

    write_jsonl(
        input_path,
        [
            {
                "source": "kraken_ws_v2",
                "depth": 10,
                "capture_ts_ns": 1780000000000000000,
                "recv_seq": 1,
                "payload": {
                    "channel": "book",
                    "type": "snapshot",
                    "data": [
                        {
                            "symbol": "BTC/USD",
                            "bids": [{"price": "45283.5", "qty": "0.10000000"}],
                            "asks": [{"price": "45285.2", "qty": "0.00100000"}],
                            "checksum": 3310070434,
                            "timestamp": "2026-07-03T10:00:00.000000Z",
                        }
                    ],
                },
            }
        ],
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "market_micstr_lab.cli.normalize",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--channel",
            "book",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Wrote 1 normalized events" in result.stdout

    events = list(read_jsonl(output_path))
    assert len(events) == 1
    assert events[0]["channel"] == "book"
    assert events[0]["event_type"] == "snapshot"
