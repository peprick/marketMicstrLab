import json
from pathlib import Path
from typing import Iterable, Iterator


def write_jsonl(path: str | Path, records: Iterable[dict]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            line = json.dumps(record, separators=(",", ":"), ensure_ascii=True)
            file.write(line + "\n")


def append_jsonl(path: str | Path, record: dict) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("a", encoding="utf-8") as file:
        line = json.dumps(record, separators=(",", ":"), ensure_ascii=True)
        file.write(line + "\n")


def read_jsonl(path: str | Path) -> Iterator[dict]:
    input_path = Path(path)

    with input_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            try:
                yield json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {input_path}") from exc
