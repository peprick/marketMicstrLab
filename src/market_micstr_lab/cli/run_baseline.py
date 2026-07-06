import argparse

from market_micstr_lab.research.baseline import (
    parse_thresholds,
    write_imbalance_baseline_report_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run baseline research models on labeled feature rows.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--train-fraction", type=float, default=0.7)
    parser.add_argument("--thresholds", default="0,0.05,0.10,0.20,0.30,0.50")

    args = parser.parse_args()

    report = write_imbalance_baseline_report_json(
        input_path=args.input,
        output_path=args.output,
        depth=args.depth,
        horizon=args.horizon,
        train_fraction=args.train_fraction,
        thresholds=parse_thresholds(args.thresholds),
    )

    test_accuracy = report["test"]["accuracy"]
    print(f"Wrote imbalance baseline report to {args.output}")
    print(f"Best threshold: {report['best_threshold']}")
    print(f"Test accuracy: {test_accuracy}")


if __name__ == "__main__":
    main()
