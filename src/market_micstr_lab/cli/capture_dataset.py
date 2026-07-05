import argparse
import asyncio
from decimal import Decimal
from pathlib import Path
from typing import Any

from market_micstr_lab.capture.kraken_ws import capture_messages
from market_micstr_lab.data.pipeline import normalize_raw_jsonl
from market_micstr_lab.research.dataset import write_labeled_feature_rows_jsonl


BOOK_CHANNEL_FLAG = 0


async def capture_dataset(
    raw_output: str | Path,
    events_output: str | Path,
    dataset_output: str | Path,
    symbol: str = "BTC/USD",
    capture_depth: int = 10,
    feature_depth: int = 1,
    max_messages: int | None = None,
    seconds: float | None = None,
    snapshot: bool = True,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
    validate: bool = False,
    capture_func: Any = capture_messages,
) -> dict[str, int]:
    raw_count = await capture_func(
        output_path=raw_output,
        channel="book",
        symbol=symbol,
        depth=capture_depth,
        snapshot=snapshot,
        max_messages=max_messages,
        seconds=seconds,
    )

    event_count = normalize_raw_jsonl(
        input_path=raw_output,
        output_path=events_output,
        book_channel_flag=BOOK_CHANNEL_FLAG,
    )

    dataset_count = write_labeled_feature_rows_jsonl(
        input_path=events_output,
        output_path=dataset_output,
        depth=feature_depth,
        horizon=horizon,
        threshold=threshold,
        validate=validate,
    )

    return {
        "raw": raw_count,
        "events": event_count,
        "dataset": dataset_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture Kraken book data, normalize it, and build labeled features."
    )
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--events-output", required=True)
    parser.add_argument("--dataset-output", required=True)
    parser.add_argument("--symbol", default="BTC/USD")
    parser.add_argument("--depth", type=int, default=10)
    parser.add_argument("--feature-depth", type=int, default=1)
    parser.add_argument("--max-messages", type=int)
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--no-snapshot", action="store_true")
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--threshold", default="0")
    parser.add_argument("--validate", action="store_true")

    args = parser.parse_args()

    if args.max_messages is None and args.seconds is None:
        parser.error("--max-messages or --seconds must be provided")

    counts = asyncio.run(
        capture_dataset(
            raw_output=args.raw_output,
            events_output=args.events_output,
            dataset_output=args.dataset_output,
            symbol=args.symbol,
            capture_depth=args.depth,
            feature_depth=args.feature_depth,
            max_messages=args.max_messages,
            seconds=args.seconds,
            snapshot=not args.no_snapshot,
            horizon=args.horizon,
            threshold=Decimal(args.threshold),
            validate=args.validate,
        )
    )

    print(f"Wrote {counts['raw']} raw Kraken messages to {args.raw_output}")
    print(f"Wrote {counts['events']} normalized book events to {args.events_output}")
    print(f"Wrote {counts['dataset']} labeled feature rows to {args.dataset_output}")


if __name__ == "__main__":
    main()
