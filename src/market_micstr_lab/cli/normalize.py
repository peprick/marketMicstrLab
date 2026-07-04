import argparse

from market_micstr_lab.data.pipeline import normalize_raw_jsonl


def channel_to_flag(channel: str) -> int:
    if channel == "book":
        return 0
    if channel == "trade":
        return 1
    raise ValueError(f"Unsupported channel: {channel}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize raw market-data JSONL.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--channel", required=True, choices=["book", "trade"])

    args = parser.parse_args()

    count = normalize_raw_jsonl(
        input_path=args.input,
        output_path=args.output,
        book_channel_flag=channel_to_flag(args.channel),
    )

    print(f"Wrote {count} normalized events to {args.output}")


if __name__ == "__main__":
    main()
