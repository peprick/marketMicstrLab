
from decimal import Decimal

from market_micstr_lab.book.order_book import OrderBook


def test_snapshot_sets_best_bid_and_ask() -> None:
    book = OrderBook()

    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["100.00", "2.5"], ["99.50", "1.0"]],
            "asks": [["100.50", "3.0"], ["101.00", "4.0"]],
        }
    )

    assert book.best_bid() == (Decimal("100.00"), Decimal("2.5"))
    assert book.best_ask() == (Decimal("100.50"), Decimal("3.0"))
    assert book.spread() == Decimal("0.50")
    assert book.mid_price() == Decimal("100.25")


def test_update_removes_best_bid() -> None:
    book = OrderBook()

    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["100.00", "2.5"], ["99.50", "1.0"]],
            "asks": [["100.50", "3.0"]],
        }
    )

    book.apply(
        {
            "channel": "book",
            "event_type": "update",
            "bids": [["100.00", "0"]],
            "asks": [],
        }
    )

    assert book.best_bid() == (Decimal("99.50"), Decimal("1.0"))


def test_update_changes_existing_level_quantity() -> None:
    book = OrderBook()

    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["100.00", "2.5"]],
            "asks": [["100.50", "3.0"]],
        }
    )

    book.apply(
        {
            "channel": "book",
            "event_type": "update",
            "bids": [["100.00", "1.25"]],
            "asks": [],
        }
    )

    assert book.best_bid() == (Decimal("100.00"), Decimal("1.25"))
