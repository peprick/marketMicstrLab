import pytest

from market_micstr_lab.book.replay import ReplayValidationError
from decimal import Decimal

from market_micstr_lab.book.order_book import OrderBook
from market_micstr_lab.book.replay import replay_events, replay_jsonl
from market_micstr_lab.data.jsonl import write_jsonl


def test_replay_events_applies_snapshot_and_update() -> None:
    book = replay_events(
        [
            {
                "channel": "book",
                "event_type": "snapshot",
                "bids": [["100.00", "2.5"], ["99.50", "1.0"]],
                "asks": [["100.50", "3.0"]],
            },
            {
                "channel": "book",
                "event_type": "update",
                "bids": [["100.00", "0"]],
                "asks": [["100.25", "1.5"]],
            },
        ]
    )

    assert book.best_bid() == (Decimal("99.50"), Decimal("1.0"))
    assert book.best_ask() == (Decimal("100.25"), Decimal("1.5"))
    assert book.spread() == Decimal("0.75")


def test_replay_jsonl_reads_events_from_file(tmp_path) -> None:
    path = tmp_path / "book_events.jsonl"

    write_jsonl(
        path,
        [
            {
                "channel": "book",
                "event_type": "snapshot",
                "bids": [["100.00", "2.5"], ["99.50", "1.0"]],
                "asks": [["100.50", "3.0"], ["101.00", "4.0"]],
            }
        ],
    )

    book = replay_jsonl(path)

    assert book.top_bids(2) == [
        (Decimal("100.00"), Decimal("2.5")),
        (Decimal("99.50"), Decimal("1.0")),
    ]
    assert book.top_asks(2) == [
        (Decimal("100.50"), Decimal("3.0")),
        (Decimal("101.00"), Decimal("4.0")),
    ]
    
    
    
    

def test_replay_validation_raises_with_recv_seq() -> None:
    events = [
        {
            "channel": "book",
            "event_type": "snapshot",
            "recv_seq": 10,
            "bids": [["101.00", "2.5"]],
            "asks": [["100.50", "3.0"]],
        }
    ]

    with pytest.raises(ReplayValidationError, match="recv_seq=10"):
        replay_events(events, validate=True)


def test_replay_without_validation_allows_crossed_book() -> None:
    book = replay_events(
        [
            {
                "channel": "book",
                "event_type": "snapshot",
                "recv_seq": 10,
                "bids": [["101.00", "2.5"]],
                "asks": [["100.50", "3.0"]],
            }
        ],
        validate=False,
    )

    assert "crossed book" in book.validation_errors()


def test_replay_checksum_validation_accepts_matching_checksum() -> None:
    event = {
        "channel": "book",
        "event_type": "snapshot",
        "recv_seq": 1,
        "bids": [["100.00", "3.0"]],
        "asks": [["100.50", "1.0"]],
    }
    expected_book = OrderBook()
    expected_book.apply(event)

    book = replay_events(
        [{**event, "checksum": expected_book.kraken_checksum()}],
        validate_checksum=True,
    )

    assert book.best_bid() == (Decimal("100.00"), Decimal("3.0"))


def test_replay_checksum_validation_raises_on_mismatch() -> None:
    events = [
        {
            "channel": "book",
            "event_type": "snapshot",
            "recv_seq": 25,
            "checksum": 123,
            "bids": [["100.00", "3.0"]],
            "asks": [["100.50", "1.0"]],
        }
    ]

    with pytest.raises(ReplayValidationError, match="checksum mismatch"):
        replay_events(events, validate_checksum=True)
