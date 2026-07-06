#include "mml/order_book.hpp"

namespace mml {

void OrderBook::apply_snapshot(const std::vector<Level>& bids, const std::vector<Level>& asks) {
    bids_.clear();
    asks_.clear();

    for (const auto& level : bids) {
        apply_level(bids_, level);
    }

    for (const auto& level : asks) {
        apply_level(asks_, level);
    }
}

void OrderBook::apply_update(Side side, Level level) {
    if (side == Side::Bid) {
        apply_level(bids_, level);
    } else {
        apply_level(asks_, level);
    }
}

void OrderBook::apply_updates(const std::vector<Level>& bids, const std::vector<Level>& asks) {
    for (const auto& level : bids) {
        apply_update(Side::Bid, level);
    }

    for (const auto& level : asks) {
        apply_update(Side::Ask, level);
    }
}

std::optional<Level> OrderBook::best_bid() const {
    if (bids_.empty()) {
        return std::nullopt;
    }

    const auto& [price, quantity] = *bids_.begin();
    return Level{price, quantity};
}

std::optional<Level> OrderBook::best_ask() const {
    if (asks_.empty()) {
        return std::nullopt;
    }

    const auto& [price, quantity] = *asks_.begin();
    return Level{price, quantity};
}

std::vector<Level> OrderBook::top_bids(std::size_t depth) const {
    std::vector<Level> levels;
    levels.reserve(depth);

    for (const auto& [price, quantity] : bids_) {
        if (levels.size() == depth) {
            break;
        }

        levels.push_back(Level{price, quantity});
    }

    return levels;
}

std::vector<Level> OrderBook::top_asks(std::size_t depth) const {
    std::vector<Level> levels;
    levels.reserve(depth);

    for (const auto& [price, quantity] : asks_) {
        if (levels.size() == depth) {
            break;
        }

        levels.push_back(Level{price, quantity});
    }

    return levels;
}

std::optional<std::int64_t> OrderBook::spread() const {
    const auto bid = best_bid();
    const auto ask = best_ask();

    if (!bid.has_value() || !ask.has_value()) {
        return std::nullopt;
    }

    return ask->price - bid->price;
}

std::optional<double> OrderBook::mid_price() const {
    const auto bid = best_bid();
    const auto ask = best_ask();

    if (!bid.has_value() || !ask.has_value()) {
        return std::nullopt;
    }

    return (static_cast<double>(bid->price) + static_cast<double>(ask->price)) / 2.0;
}

std::vector<std::string> OrderBook::validation_errors() const {
    std::vector<std::string> errors;

    if (bids_.empty()) {
        errors.push_back("missing bids");
    }

    if (asks_.empty()) {
        errors.push_back("missing asks");
    }

    const auto bid = best_bid();
    const auto ask = best_ask();

    if (bid.has_value() && ask.has_value() && bid->price >= ask->price) {
        errors.push_back("crossed book");
    }

    return errors;
}

bool OrderBook::is_valid() const {
    return validation_errors().empty();
}

std::size_t OrderBook::bid_level_count() const {
    return bids_.size();
}

std::size_t OrderBook::ask_level_count() const {
    return asks_.size();
}

}  // namespace mml
