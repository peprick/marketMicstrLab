from pathlib import Path
from typing import Iterable

from market_micstr_lab.book.order_book import OrderBook
from market_micstr_lab.data.jsonl import read_jsonl


class ReplayValidationError(ValueError):
    def __init__(self, event_index: int, event: dict, errors: list[str]) -> None:
        self.event_index = event_index
        self.event = event
        self.errors = errors
        recv_seq = event.get("recv_seq", "unknown")
        message = f"Invalid book after event_index={event_index}, recv_seq={recv_seq}: {'; '.join(errors)}"
        super().__init__(message)


def replay_events(events: Iterable[dict], validate: bool = False) -> OrderBook:
    book = OrderBook()

    for event_index, event in enumerate(events):
        book.apply(event)

        if validate:
            errors = book.validation_errors()
            if errors:
                raise ReplayValidationError(event_index, event, errors)

    return book


def replay_jsonl(path: str | Path, validate: bool = False) -> OrderBook:
    return replay_events(read_jsonl(path), validate=validate)
