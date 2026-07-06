#pragma once

#include <cstdint>
#include <functional>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace mml {

struct Level {
    std::int64_t price;
    std::int64_t quantity;

    bool operator==(const Level&) const = default;
};

enum class Side {
    Bid,
    Ask,
};

class OrderBook {
public:
    void apply_snapshot(const std::vector<Level>& bids, const std::vector<Level>& asks);
    void apply_update(Side side, Level level);
    void apply_updates(const std::vector<Level>& bids, const std::vector<Level>& asks);

    std::optional<Level> best_bid() const;
    std::optional<Level> best_ask() const;

    std::vector<Level> top_bids(std::size_t depth) const;
    std::vector<Level> top_asks(std::size_t depth) const;

    std::optional<std::int64_t> spread() const;
    std::optional<double> mid_price() const;

    std::vector<std::string> validation_errors() const;
    bool is_valid() const;

    std::size_t bid_level_count() const;
    std::size_t ask_level_count() const;

private:
    using BidMap = std::map<std::int64_t, std::int64_t, std::greater<std::int64_t>>;
    using AskMap = std::map<std::int64_t, std::int64_t>;

    BidMap bids_;
    AskMap asks_;

    template <typename BookSide>
    static void apply_level(BookSide& side, Level level) {
        if (level.price <= 0) {
            throw std::invalid_argument("price must be positive");
        }

        if (level.quantity < 0) {
            throw std::invalid_argument("quantity cannot be negative");
        }

        if (level.quantity == 0) {
            side.erase(level.price);
            return;
        }

        side[level.price] = level.quantity;
    }
};

}  // namespace mml
