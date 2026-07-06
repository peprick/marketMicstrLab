import argparse

from market_micstr_lab.research.baseline import parse_thresholds
from market_micstr_lab.research.walk_forward import write_walk_forward_report_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run walk-forward validation for imbalance baseline.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--train-size", type=int, default=1000)
    parser.add_argument("--test-size", type=int, default=200)
    parser.add_argument("--step-size", type=int, default=200)
    parser.add_argument("--thresholds", default="0,0.05,0.10,0.20,0.30,0.50")

    args = parser.parse_args()

    report = write_walk_forward_report_json(
        input_path=args.input,
        output_path=args.output,
        depth=args.depth,
        horizon=args.horizon,
        train_size=args.train_size,
        test_size=args.test_size,
        step_size=args.step_size,
        thresholds=parse_thresholds(args.thresholds),
    )

    print(f"Wrote walk-forward report to {args.output}")
    print(f"Windows: {report['window_count']}")
    print(f"Mean test accuracy: {report['mean_test_accuracy']}")


if __name__ == "__main__":
    main()
