
from pathlib import Path

from market_micstr_lab.data.jsonl import read_jsonl, write_jsonl
from market_micstr_lab.data.normalize import normalize_message


def normalize_raw_jsonl(
    input_path: str | Path,
    output_path: str | Path,
    book_channel_flag: int,
) -> int:
    normalized_events = []

    for raw_envelope in read_jsonl(input_path):
        events = normalize_message(raw_envelope, book_channel_flag)
        normalized_events.extend(events)

    write_jsonl(output_path, normalized_events)

    return len(normalized_events)
