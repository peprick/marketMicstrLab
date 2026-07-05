import argparse
import asyncio

from market_micstr_lab.capture.kraken_ws import capture_messages


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture raw Kraken WebSocket messages to JSONL.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--channel", required=True, choices=["book", "trade"])
    parser.add_argument("--symbol", default="BTC/USD")
    parser.add_argument("--depth", type=int, default=10)
    parser.add_argument("--max-messages", type=int)
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--no-snapshot", action="store_true")

    args = parser.parse_args()

    count = asyncio.run(
        capture_messages(
            output_path=args.output,
            channel=args.channel,
            symbol=args.symbol,
            depth=args.depth,
            snapshot=not args.no_snapshot,
            max_messages=args.max_messages,
            seconds=args.seconds,
        )
    )

    print(f"Wrote {count} raw Kraken messages to {args.output}")


if __name__ == "__main__":
    main()
