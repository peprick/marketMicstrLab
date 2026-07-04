
from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl
from market_micstr_lab.data.pipeline import normalize_raw_jsonl


def test_normalize_raw_book_jsonl(tmp_path) -> None:
    input_path = tmp_path / "raw_book.jsonl"
    output_path = tmp_path / "processed_book.jsonl"

    raw_records = [
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
        },
        {
            "source": "kraken_ws_v2",
            "depth": 10,
            "capture_ts_ns": 1780000000000000001,
            "recv_seq": 2,
            "payload": {
                "channel": "book",
                "type": "update",
                "data": [
                    {
                        "symbol": "BTC/USD",
                        "bids": [{"price": "45283.5", "qty": "0.00000000"}],
                        "asks": [],
                        "checksum": 3310070435,
                        "timestamp": "2026-07-03T10:00:01.000000Z",
                    }
                ],
            },
        },
    ]

    write_jsonl(input_path, raw_records)

    count = normalize_raw_jsonl(input_path, output_path, book_channel_flag=0)

    events = list(read_jsonl(output_path))
    assert count == 2
    assert len(events) == 2
    assert events[0]["event_type"] == "snapshot"
    assert events[1]["event_type"] == "update"
    assert events[1]["bids"] == [["45283.5", "0.00000000"]]


def test_normalize_raw_trade_jsonl(tmp_path) -> None:
    input_path = tmp_path / "raw_trade.jsonl"
    output_path = tmp_path / "processed_trade.jsonl"

    raw_records = [
        {
            "source": "kraken_ws_v2",
            "capture_ts_ns": 1780000000000000002,
            "recv_seq": 3,
            "payload": {
                "channel": "trade",
                "type": "update",
                "data": [
                    {
                        "symbol": "BTC/USD",
                        "side": "sell",
                        "price": "45280.0",
                        "qty": "0.050",
                        "ord_type": "market",
                        "trade_id": 123456790,
                        "timestamp": "2026-07-03T10:00:02.000000Z",
                    }
                ],
            },
        }
    ]

    write_jsonl(input_path, raw_records)

    count = normalize_raw_jsonl(input_path, output_path, book_channel_flag=1)

    events = list(read_jsonl(output_path))
    assert count == 1
    assert events[0]["channel"] == "trade"
    assert events[0]["side"] == "sell"
    assert events[0]["price"] == "45280.0"
