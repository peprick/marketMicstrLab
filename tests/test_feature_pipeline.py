
import pytest

from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl
from market_micstr_lab.features.pipeline import (
    feature_row_from_event,
    feature_rows_from_events,
    write_feature_rows_jsonl,
)
from market_micstr_lab.book.order_book import OrderBook


def test_feature_row_from_event_includes_metadata_and_features() -> None:
    book = OrderBook()
    event = {
        "channel": "book",
        "event_type": "snapshot",
        "recv_seq": 1,
        "exchange_ts": "2026-07-03T10:00:00.000000Z",
        "symbol": "BTC/USD",
        "bids": [["100.00", "3.0"]],
        "asks": [["100.50", "1.0"]],
    }

    book.apply(event)
    row = feature_row_from_event(event, book, depth=1)

    assert row["recv_seq"] == 1
    assert row["exchange_ts"] == "2026-07-03T10:00:00.000000Z"
    assert row["symbol"] == "BTC/USD"
    assert row["best_bid_price"] == "100.00"
    assert row["best_ask_price"] == "100.50"
    assert row["spread"] == "0.50"
    assert row["mid_price"] == "100.25"
    assert row["imbalance_1"] == "0.5"
    assert row["is_valid"] is True


def test_feature_rows_from_events_outputs_row_after_each_event() -> None:
    rows = feature_rows_from_events(
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
                "bids": [["100.00", "1.0"]],
                "asks": [],
            },
        ],
        depth=1,
    )

    assert len(rows) == 2
    assert rows[0]["imbalance_1"] == "0.5"
    assert rows[1]["imbalance_1"] == "0"


def test_feature_rows_validation_raises_on_crossed_book() -> None:
    events = [
        {
            "channel": "book",
            "event_type": "snapshot",
            "recv_seq": 1,
            "symbol": "BTC/USD",
            "bids": [["101.00", "1.0"]],
            "asks": [["100.50", "1.0"]],
        }
    ]

    with pytest.raises(ValueError, match="crossed book"):
        feature_rows_from_events(events, validate=True)


def test_write_feature_rows_jsonl(tmp_path) -> None:
    input_path = tmp_path / "book_events.jsonl"
    output_path = tmp_path / "features.jsonl"

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
            }
        ],
    )

    count = write_feature_rows_jsonl(input_path, output_path, depth=1)

    rows = list(read_jsonl(output_path))
    assert count == 1
    assert rows[0]["mid_price"] == "100.25"
    assert rows[0]["microprice"] == "100.375"
