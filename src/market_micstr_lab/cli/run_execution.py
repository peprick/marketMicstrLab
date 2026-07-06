import argparse
from decimal import Decimal

from market_micstr_lab.research.execution import write_execution_report_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cost-aware execution simulation.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--threshold", default="0")
    parser.add_argument("--fee-bps", default="0")
    parser.add_argument("--slippage-bps", default="0")

    args = parser.parse_args()

    report = write_execution_report_json(
        input_path=args.input,
        output_path=args.output,
        depth=args.depth,
        horizon=args.horizon,
        threshold=Decimal(args.threshold),
        fee_bps=Decimal(args.fee_bps),
        slippage_bps=Decimal(args.slippage_bps),
    )

    summary = report["summary"]

    print(f"Wrote execution report to {args.output}")
    print(f"Trades: {summary['trade_count']}")
    print(f"Total net PnL: {summary['total_net_pnl']}")


if __name__ == "__main__":
    main()
