from decimal import Decimal

import pytest

from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl
from market_micstr_lab.research.dataset import (
    build_labeled_feature_rows,
    write_labeled_feature_rows_jsonl,
)


def test_build_labeled_feature_rows() -> None:
    events = [
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
    ]

    from tempfile import NamedTemporaryFile
    from market_micstr_lab.data.jsonl import write_jsonl

    with NamedTemporaryFile(mode="w+", suffix=".jsonl") as file:
        write_jsonl(file.name, events)
        rows = build_labeled_feature_rows(file.name, depth=1, horizon=1)

    assert len(rows) == 2
    assert rows[0]["mid_price"] == "100.25"
    assert rows[0]["future_mid_price_1"] == "100.75"
    assert rows[0]["mid_price_direction_1"] == 1
    assert rows[1]["future_mid_price_1"] is None


def test_write_labeled_feature_rows_jsonl(tmp_path) -> None:
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
                "bids": [["100.00", "0"], ["99.50", "3.0"]],
                "asks": [["100.00", "1.0"]],
            },
        ],
    )

    count = write_labeled_feature_rows_jsonl(input_path, output_path, depth=1, horizon=1)

    rows = list(read_jsonl(output_path))
    assert count == 2
    assert rows[0]["mid_price_delta_1"] == "-0.50"
    assert rows[0]["mid_price_direction_1"] == -1


def test_build_labeled_feature_rows_validation() -> None:
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

    from tempfile import NamedTemporaryFile
    from market_micstr_lab.data.jsonl import write_jsonl

    with NamedTemporaryFile(mode="w+", suffix=".jsonl") as file:
        write_jsonl(file.name, events)

        with pytest.raises(ValueError, match="crossed book"):
            build_labeled_feature_rows(file.name, validate=True)
