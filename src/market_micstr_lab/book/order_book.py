from decimal import Decimal
from zlib import crc32


def _kraken_checksum_value(value: Decimal) -> str:
    normalized = format(value, "f").replace(".", "").lstrip("0")
    return normalized or "0"


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

            if price <= 0:
                raise ValueError(f"Price must be positive: {price}")

            if qty < 0:
                raise ValueError(f"Quantity cannot be negative: {qty}")

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
        
        
        
    def top_bids(self, n: int) -> list[tuple[Decimal, Decimal]]:
        return [(price, self.bids[price]) for price in sorted(self.bids, reverse=True)[:n]]




    def top_asks(self, n: int) -> list[tuple[Decimal, Decimal]]:
        return [(price, self.asks[price]) for price in sorted(self.asks)[:n]]
        
        
        
    def kraken_checksum(self, depth: int = 10) -> int:
        checksum_parts = []

        for price, qty in self.top_asks(depth):
            checksum_parts.append(_kraken_checksum_value(price))
            checksum_parts.append(_kraken_checksum_value(qty))

        for price, qty in self.top_bids(depth):
            checksum_parts.append(_kraken_checksum_value(price))
            checksum_parts.append(_kraken_checksum_value(qty))

        checksum_input = "".join(checksum_parts).encode("ascii")
        return crc32(checksum_input) & 0xFFFFFFFF


    def checksum_errors(self, event: dict, depth: int = 10) -> list[str]:
        exchange_checksum = event.get("checksum")
        if exchange_checksum is None:
            return []

        try:
            expected_checksum = int(exchange_checksum)
        except (TypeError, ValueError):
            return [f"invalid checksum value: {exchange_checksum}"]

        local_checksum = self.kraken_checksum(depth=depth)
        if local_checksum != expected_checksum:
            return [
                f"checksum mismatch: exchange={expected_checksum}, local={local_checksum}"
            ]

        return []


        
        
    
    def validation_errors(self) -> list[str]:
        errors = []

        if not self.bids:
            errors.append("missing bids")

        if not self.asks:
            errors.append("missing asks")

        best_bid = self.best_bid()
        best_ask = self.best_ask()

        if best_bid is not None and best_ask is not None and best_bid[0] >= best_ask[0]:
            errors.append("crossed book")

        return errors




    def is_valid(self) -> bool:
        return not self.validation_errors()


    def assert_valid(self) -> None:
        errors = self.validation_errors()
        if errors:
            raise ValueError("; ".join(errors))
