from decimal import Decimal
from pathlib import Path

from market_micstr_lab.data.jsonl import write_jsonl
from market_micstr_lab.features.pipeline import feature_rows_from_jsonl
from market_micstr_lab.research.labels import add_future_mid_price_labels


def build_labeled_feature_rows(
    input_path: str | Path,
    depth: int = 1,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
    validate: bool = False,
) -> list[dict]:
    feature_rows = feature_rows_from_jsonl(
        input_path,
        depth=depth,
        validate=validate,
    )

    return add_future_mid_price_labels(
        feature_rows,
        horizon=horizon,
        threshold=threshold,
    )


def write_labeled_feature_rows_jsonl(
    input_path: str | Path,
    output_path: str | Path,
    depth: int = 1,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
    validate: bool = False,
) -> int:
    rows = build_labeled_feature_rows(
        input_path,
        depth=depth,
        horizon=horizon,
        threshold=threshold,
        validate=validate,
    )

    write_jsonl(output_path, rows)
    return len(rows)
