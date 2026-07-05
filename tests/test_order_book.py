import pytest
from decimal import Decimal
from zlib import crc32

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


def test_kraken_checksum_uses_top_asks_then_bids() -> None:
    book = OrderBook()

    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["100.00", "3.0"], ["99.50", "1.25"]],
            "asks": [["100.50", "0.0100"], ["101.00", "2"]],
        }
    )

    checksum_input = "1005010010100210000309950125"
    expected_checksum = crc32(checksum_input.encode("ascii")) & 0xFFFFFFFF

    assert book.kraken_checksum(depth=10) == expected_checksum


def test_checksum_errors_compare_event_checksum() -> None:
    book = OrderBook()
    event = {
        "channel": "book",
        "event_type": "snapshot",
        "bids": [["100.00", "3.0"]],
        "asks": [["100.50", "1.0"]],
    }

    book.apply(event)
    checksum = book.kraken_checksum()

    assert book.checksum_errors({**event, "checksum": checksum}) == []
    assert book.checksum_errors({**event, "checksum": checksum + 1}) == [
        f"checksum mismatch: exchange={checksum + 1}, local={checksum}"
    ]
    
    
    
    

def test_validation_detects_missing_side() -> None:
    book = OrderBook()

    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["100.00", "2.5"]],
            "asks": [],
        }
    )

    assert book.validation_errors() == ["missing asks"]
    assert not book.is_valid()





def test_validation_detects_crossed_book() -> None:
    book = OrderBook()

    book.apply(
        {
            "channel": "book",
            "event_type": "snapshot",
            "bids": [["101.00", "2.5"]],
            "asks": [["100.50", "3.0"]],
        }
    )

    assert "crossed book" in book.validation_errors()

    with pytest.raises(ValueError, match="crossed book"):
        book.assert_valid()


def test_negative_quantity_is_rejected() -> None:
    book = OrderBook()

    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        book.apply(
            {
                "channel": "book",
                "event_type": "snapshot",
                "bids": [["100.00", "-1.0"]],
                "asks": [["100.50", "3.0"]],
            }
        )


def test_zero_price_is_rejected() -> None:
    book = OrderBook()

    with pytest.raises(ValueError, match="Price must be positive"):
        book.apply(
            {
                "channel": "book",
                "event_type": "snapshot",
                "bids": [["0", "1.0"]],
                "asks": [["100.50", "3.0"]],
            }
        )
