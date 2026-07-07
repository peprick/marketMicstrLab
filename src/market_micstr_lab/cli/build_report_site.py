import argparse

from market_micstr_lab.research.report_site import build_report_site


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local static research report UI.")
    parser.add_argument("--reports-dir", required=True)
    parser.add_argument("--output")

    args = parser.parse_args()

    output_path = build_report_site(
        reports_dir=args.reports_dir,
        output_path=args.output,
    )

    print(f"Wrote report site to {output_path}")


if __name__ == "__main__":
    main()
