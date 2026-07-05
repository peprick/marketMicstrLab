import argparse
from decimal import Decimal

from market_micstr_lab.research.dataset import write_labeled_feature_rows_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Build labeled feature rows from book event JSONL.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--threshold", default="0")
    parser.add_argument("--validate", action="store_true")

    args = parser.parse_args()

    count = write_labeled_feature_rows_jsonl(
        input_path=args.input,
        output_path=args.output,
        depth=args.depth,
        horizon=args.horizon,
        threshold=Decimal(args.threshold),
        validate=args.validate,
    )

    print(f"Wrote {count} labeled feature rows to {args.output}")


if __name__ == "__main__":
    main()
