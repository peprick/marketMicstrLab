
from decimal import Decimal

from market_micstr_lab.book.order_book import OrderBook
from market_micstr_lab.features.book_features import (
    book_feature_snapshot,
    book_imbalance,
    microprice,
    side_depth,
)


def test_side_depth_sums_quantities() -> None:
    levels = [
        (Decimal("100.00"), Decimal("2.5")),
        (Decimal("99.50"), Decimal("1.5")),
    ]

    assert side_depth(levels) == Decimal("4.0")


def test_book_imbalance_uses_top_n_depth() -> None:
    book = OrderBook()
    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["100.00", "3.0"], ["99.50", "1.0"]],
            "asks": [["100.50", "1.0"], ["101.00", "1.0"]],
        }
    )

    assert book_imbalance(book, depth=1) == Decimal("0.5")
    assert book_imbalance(book, depth=2) == Decimal("0.3333333333333333333333333333")


def test_microprice_weights_by_top_of_book_quantity() -> None:
    book = OrderBook()
    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["100.00", "3.0"]],
            "asks": [["101.00", "1.0"]],
        }
    )

    assert microprice(book) == Decimal("100.75")


def test_book_feature_snapshot_contains_core_fields() -> None:
    book = OrderBook()
    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["100.00", "3.0"], ["99.50", "1.0"]],
            "asks": [["100.50", "1.0"], ["101.00", "1.0"]],
        }
    )

    features = book_feature_snapshot(book, depth=2)

    assert features["best_bid_price"] == Decimal("100.00")
    assert features["best_ask_price"] == Decimal("100.50")
    assert features["spread"] == Decimal("0.50")
    assert features["mid_price"] == Decimal("100.25")
    assert features["bid_depth_2"] == Decimal("4.0")
    assert features["ask_depth_2"] == Decimal("2.0")
    assert features["imbalance_2"] == Decimal("0.3333333333333333333333333333")
    assert features["is_valid"] is True
