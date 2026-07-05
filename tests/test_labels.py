
from decimal import Decimal

import pytest

from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl
from market_micstr_lab.research.labels import (
    add_future_mid_price_labels,
    mid_price_direction,
    write_labeled_rows_jsonl,
)


def test_mid_price_direction() -> None:
    assert mid_price_direction("100.00", "100.50") == 1
    assert mid_price_direction("100.50", "100.00") == -1
    assert mid_price_direction("100.00", "100.00") == 0
    assert mid_price_direction(None, "100.00") is None


def test_mid_price_direction_with_threshold() -> None:
    assert mid_price_direction("100.00", "100.01", threshold=Decimal("0.05")) == 0
    assert mid_price_direction("100.00", "100.10", threshold=Decimal("0.05")) == 1


def test_add_future_mid_price_labels_horizon_1() -> None:
    rows = [
        {"recv_seq": 1, "mid_price": "100.00"},
        {"recv_seq": 2, "mid_price": "100.50"},
        {"recv_seq": 3, "mid_price": "100.25"},
    ]

    labeled = add_future_mid_price_labels(rows, horizon=1)

    assert labeled[0]["future_mid_price_1"] == "100.50"
    assert labeled[0]["mid_price_delta_1"] == "0.50"
    assert labeled[0]["mid_price_direction_1"] == 1

    assert labeled[1]["future_mid_price_1"] == "100.25"
    assert labeled[1]["mid_price_delta_1"] == "-0.25"
    assert labeled[1]["mid_price_direction_1"] == -1

    assert labeled[2]["future_mid_price_1"] is None
    assert labeled[2]["mid_price_delta_1"] is None
    assert labeled[2]["mid_price_direction_1"] is None


def test_add_future_mid_price_labels_rejects_invalid_horizon() -> None:
    with pytest.raises(ValueError, match="horizon must be positive"):
        add_future_mid_price_labels([], horizon=0)


def test_write_labeled_rows_jsonl(tmp_path) -> None:
    input_path = tmp_path / "features.jsonl"
    output_path = tmp_path / "labeled.jsonl"

    write_jsonl(
        input_path,
        [
            {"recv_seq": 1, "mid_price": "100.00"},
            {"recv_seq": 2, "mid_price": "100.50"},
        ],
    )

    count = write_labeled_rows_jsonl(input_path, output_path, horizon=1)

    rows = list(read_jsonl(output_path))
    assert count == 2
    assert rows[0]["mid_price_direction_1"] == 1
    assert rows[1]["mid_price_direction_1"] is None
