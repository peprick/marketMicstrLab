from decimal import Decimal
from pathlib import Path
from typing import Iterable

from market_micstr_lab.book.order_book import OrderBook
from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl
from market_micstr_lab.features.book_features import book_feature_snapshot


def _json_value(value):
    if isinstance(value, Decimal):
        return str(value)
    return value


def feature_row_from_event(event: dict, book: OrderBook, depth: int = 1) -> dict:
    features = book_feature_snapshot(book, depth=depth)

    row = {
        "recv_seq": event.get("recv_seq"),
        "exchange_ts": event.get("exchange_ts"),
        "event_type": event.get("event_type"),
        "symbol": event.get("symbol"),
        "feature_depth": depth,
    }

    row.update({key: _json_value(value) for key, value in features.items()})
    return row


def feature_rows_from_events(
    events: Iterable[dict],
    depth: int = 1,
    validate: bool = False,
) -> list[dict]:
    book = OrderBook()
    rows = []

    for event in events:
        book.apply(event)

        if validate:
            book.assert_valid()

        rows.append(feature_row_from_event(event, book, depth=depth))

    return rows


def feature_rows_from_jsonl(
    input_path: str | Path,
    depth: int = 1,
    validate: bool = False,
) -> list[dict]:
    return feature_rows_from_events(
        read_jsonl(input_path),
        depth=depth,
        validate=validate,
    )


def write_feature_rows_jsonl(
    input_path: str | Path,
    output_path: str | Path,
    depth: int = 1,
    validate: bool = False,
) -> int:
    rows = feature_rows_from_jsonl(input_path, depth=depth, validate=validate)
    write_jsonl(output_path, rows)
    return len(rows)
