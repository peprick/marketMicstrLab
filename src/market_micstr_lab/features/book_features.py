from decimal import Decimal

from market_micstr_lab.book.order_book import OrderBook


def side_depth(levels: list[tuple[Decimal, Decimal]]) -> Decimal:
    return sum((qty for _, qty in levels), Decimal("0"))


def book_imbalance(book: OrderBook, depth: int = 1) -> Decimal | None:
    bid_depth = side_depth(book.top_bids(depth))
    ask_depth = side_depth(book.top_asks(depth))
    total_depth = bid_depth + ask_depth

    if total_depth == 0:
        return None

    return (bid_depth - ask_depth) / total_depth


def microprice(book: OrderBook) -> Decimal | None:
    best_bid = book.best_bid()
    best_ask = book.best_ask()

    if best_bid is None or best_ask is None:
        return None

    bid_price, bid_qty = best_bid
    ask_price, ask_qty = best_ask
    total_qty = bid_qty + ask_qty

    if total_qty == 0:
        return None

    return ((ask_price * bid_qty) + (bid_price * ask_qty)) / total_qty


def book_feature_snapshot(book: OrderBook, depth: int = 1) -> dict:
    best_bid = book.best_bid()
    best_ask = book.best_ask()

    return {
        "best_bid_price": best_bid[0] if best_bid else None,
        "best_bid_qty": best_bid[1] if best_bid else None,
        "best_ask_price": best_ask[0] if best_ask else None,
        "best_ask_qty": best_ask[1] if best_ask else None,
        "spread": book.spread(),
        "mid_price": book.mid_price(),
        "microprice": microprice(book),
        f"bid_depth_{depth}": side_depth(book.top_bids(depth)),
        f"ask_depth_{depth}": side_depth(book.top_asks(depth)),
        f"imbalance_{depth}": book_imbalance(book, depth),
        "is_valid": book.is_valid(),
    }
