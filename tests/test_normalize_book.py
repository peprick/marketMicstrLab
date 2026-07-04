from market_micstr_lab.data.normalize import normalize_message


def test_normalize_book_snapshot() -> None:
    raw = {
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

    events = normalize_message(raw, 0)

    assert len(events) == 1
    event = events[0]
    assert event["channel"] == "book"
    assert event["event_type"] == "snapshot"
    assert event["symbol"] == "BTC/USD"
    assert event["depth"] == 10
    assert event["bids"] == [["45283.5", "0.10000000"]]
    assert event["asks"] == [["45285.2", "0.00100000"]]
    assert event["checksum"] == 3310070434
