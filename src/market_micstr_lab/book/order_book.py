
from decimal import Decimal


class OrderBook:
    def __init__(self) -> None:
        self.bids: dict[Decimal, Decimal] = {}
        self.asks: dict[Decimal, Decimal] = {}

    def apply(self, event: dict) -> None:
        if event["channel"] != "book":
            raise ValueError(f"Expected book event, got {event['channel']}")

        if event["event_type"] == "snapshot":
            self.bids.clear()
            self.asks.clear()

        if event["event_type"] not in {"snapshot", "update"}:
            raise ValueError(f"Unsupported event type: {event['event_type']}")

        self._apply_levels(self.bids, event.get("bids", []))
        self._apply_levels(self.asks, event.get("asks", []))

    def _apply_levels(self, side: dict[Decimal, Decimal], levels: list[list[str]]) -> None:
        for price_str, qty_str in levels:
            price = Decimal(price_str)
            qty = Decimal(qty_str)

            if qty == 0:
                side.pop(price, None)
            else:
                side[price] = qty

    def best_bid(self) -> tuple[Decimal, Decimal] | None:
        if not self.bids:
            return None

        price = max(self.bids)
        return price, self.bids[price]

    def best_ask(self) -> tuple[Decimal, Decimal] | None:
        if not self.asks:
            return None

        price = min(self.asks)
        return price, self.asks[price]

    def spread(self) -> Decimal | None:
        best_bid = self.best_bid()
        best_ask = self.best_ask()

        if best_bid is None or best_ask is None:
            return None

        return best_ask[0] - best_bid[0]

    def mid_price(self) -> Decimal | None:
        best_bid = self.best_bid()
        best_ask = self.best_ask()

        if best_bid is None or best_ask is None:
            return None

        return (best_bid[0] + best_ask[0]) / Decimal("2")
