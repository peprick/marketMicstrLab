
from decimal import Decimal
from pathlib import Path
from typing import Any

from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _json_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return str(value)


def mid_price_direction(
    current_mid: Any,
    future_mid: Any,
    threshold: Decimal = Decimal("0"),
) -> int | None:
    current = _to_decimal(current_mid)
    future = _to_decimal(future_mid)

    if current is None or future is None:
        return None

    delta = future - current

    if delta > threshold:
        return 1
    if delta < -threshold:
        return -1
    return 0


def add_future_mid_price_labels(
    rows: list[dict],
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
) -> list[dict]:
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    labeled_rows = []

    for index, row in enumerate(rows):
        labeled = dict(row)
        future_index = index + horizon

        current_mid = _to_decimal(row.get("mid_price"))
        future_mid = None

        if future_index < len(rows):
            future_mid = _to_decimal(rows[future_index].get("mid_price"))

        delta = None
        if current_mid is not None and future_mid is not None:
            delta = future_mid - current_mid

        labeled[f"future_mid_price_{horizon}"] = _json_decimal(future_mid)
        labeled[f"mid_price_delta_{horizon}"] = _json_decimal(delta)
        labeled[f"mid_price_direction_{horizon}"] = mid_price_direction(
            current_mid,
            future_mid,
            threshold=threshold,
        )

        labeled_rows.append(labeled)

    return labeled_rows


def write_labeled_rows_jsonl(
    input_path: str | Path,
    output_path: str | Path,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
) -> int:
    rows = list(read_jsonl(input_path))
    labeled_rows = add_future_mid_price_labels(
        rows,
        horizon=horizon,
        threshold=threshold,
    )
    write_jsonl(output_path, labeled_rows)
    return len(labeled_rows)
