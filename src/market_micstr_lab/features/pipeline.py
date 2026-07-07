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


def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _decimal_stddev(values: list[Decimal]) -> Decimal | None:
    if not values:
        return None

    mean = sum(values, Decimal("0")) / Decimal(len(values))
    variance = sum(((value - mean) ** 2 for value in values), Decimal("0")) / Decimal(len(values))
    return Decimal(str(float(variance) ** 0.5))


def _order_flow_imbalance(row: dict, previous: dict | None) -> Decimal | None:
    if previous is None:
        return None

    bid_price = _to_decimal(row.get("best_bid_price"))
    bid_qty = _to_decimal(row.get("best_bid_qty"))
    ask_price = _to_decimal(row.get("best_ask_price"))
    ask_qty = _to_decimal(row.get("best_ask_qty"))
    prev_bid_price = _to_decimal(previous.get("best_bid_price"))
    prev_bid_qty = _to_decimal(previous.get("best_bid_qty"))
    prev_ask_price = _to_decimal(previous.get("best_ask_price"))
    prev_ask_qty = _to_decimal(previous.get("best_ask_qty"))

    if None in {
        bid_price,
        bid_qty,
        ask_price,
        ask_qty,
        prev_bid_price,
        prev_bid_qty,
        prev_ask_price,
        prev_ask_qty,
    }:
        return None

    if bid_price > prev_bid_price:
        bid_contribution = bid_qty
    elif bid_price < prev_bid_price:
        bid_contribution = -prev_bid_qty
    else:
        bid_contribution = bid_qty - prev_bid_qty

    if ask_price < prev_ask_price:
        ask_contribution = ask_qty
    elif ask_price > prev_ask_price:
        ask_contribution = -prev_ask_qty
    else:
        ask_contribution = -(ask_qty - prev_ask_qty)

    return bid_contribution + ask_contribution


def enrich_feature_rows(rows: list[dict], rolling_window: int = 10) -> list[dict]:
    if rolling_window <= 0:
        raise ValueError("rolling_window must be positive")

    enriched_rows = []
    mid_changes: list[Decimal] = []

    for index, row in enumerate(rows):
        enriched = dict(row)
        previous = enriched_rows[-1] if enriched_rows else None

        current_mid = _to_decimal(row.get("mid_price"))
        previous_mid = _to_decimal(previous.get("mid_price")) if previous else None
        current_spread = _to_decimal(row.get("spread"))
        previous_spread = _to_decimal(previous.get("spread")) if previous else None

        mid_change = None
        mid_return = None
        if current_mid is not None and previous_mid is not None:
            mid_change = current_mid - previous_mid
            if previous_mid != 0:
                mid_return = mid_change / previous_mid

        spread_change = None
        if current_spread is not None and previous_spread is not None:
            spread_change = current_spread - previous_spread

        if mid_change is not None:
            mid_changes.append(mid_change)

        window_changes = mid_changes[-rolling_window:]
        enriched["mid_price_change_1"] = _json_value(mid_change)
        enriched["mid_price_return_1"] = _json_value(mid_return)
        enriched["spread_change_1"] = _json_value(spread_change)
        enriched[f"event_count_{rolling_window}"] = min(index + 1, rolling_window)
        enriched[f"rolling_mid_volatility_{rolling_window}"] = _json_value(
            _decimal_stddev(window_changes)
        )
        enriched["order_flow_imbalance_1"] = _json_value(
            _order_flow_imbalance(row, previous)
        )

        enriched_rows.append(enriched)

    return enriched_rows


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
    validate_checksum: bool = False,
    checksum_depth: int = 10,
) -> list[dict]:
    book = OrderBook()
    rows = []

    for event in events:
        book.apply(event)

        if validate:
            book.assert_valid()

        if validate_checksum:
            checksum_errors = book.checksum_errors(event, depth=checksum_depth)
            if checksum_errors:
                raise ValueError("; ".join(checksum_errors))

        rows.append(feature_row_from_event(event, book, depth=depth))

    return enrich_feature_rows(rows)


def feature_rows_from_jsonl(
    input_path: str | Path,
    depth: int = 1,
    validate: bool = False,
    validate_checksum: bool = False,
    checksum_depth: int = 10,
) -> list[dict]:
    return feature_rows_from_events(
        read_jsonl(input_path),
        depth=depth,
        validate=validate,
        validate_checksum=validate_checksum,
        checksum_depth=checksum_depth,
    )


def write_feature_rows_jsonl(
    input_path: str | Path,
    output_path: str | Path,
    depth: int = 1,
    validate: bool = False,
    validate_checksum: bool = False,
    checksum_depth: int = 10,
) -> int:
    rows = feature_rows_from_jsonl(
        input_path,
        depth=depth,
        validate=validate,
        validate_checksum=validate_checksum,
        checksum_depth=checksum_depth,
    )
    write_jsonl(output_path, rows)
    return len(rows)
