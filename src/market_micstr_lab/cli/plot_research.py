import argparse

from market_micstr_lab.research.charts import write_research_charts


def main() -> None:
    parser = argparse.ArgumentParser(description="Write research SVG charts from labeled feature rows.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--imbalance-depth", type=int, default=1)

    args = parser.parse_args()

    paths = write_research_charts(
        dataset_path=args.dataset,
        baseline_path=args.baseline,
        output_dir=args.output_dir,
        imbalance_depth=args.imbalance_depth,
    )

    for name, path in paths.items():
        print(f"Wrote {name} chart to {path}")


if __name__ == "__main__":
    main()
