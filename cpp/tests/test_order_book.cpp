#include "mml/order_book.hpp"

#include <cassert>
#include <stdexcept>
#include <vector>

namespace {

void test_snapshot_sets_best_bid_and_ask() {
    mml::OrderBook book;

    book.apply_snapshot(
        {
            {10000, 250},
            {9950, 100},
        },
        {
            {10050, 300},
            {10100, 400},
        }
    );

    const auto bid = book.best_bid();
    const auto ask = book.best_ask();

    assert(bid.has_value());
    assert(ask.has_value());
    assert(*bid == (mml::Level{10000, 250}));
    assert(*ask == (mml::Level{10050, 300}));
    assert(book.spread().value() == 50);
    assert(book.mid_price().value() == 10025.0);
    assert(book.is_valid());
}

void test_update_removes_best_bid() {
    mml::OrderBook book;

    book.apply_snapshot(
        {
            {10000, 250},
            {9950, 100},
        },
        {
            {10050, 300},
        }
    );

    book.apply_update(mml::Side::Bid, {10000, 0});

    const auto bid = book.best_bid();

    assert(bid.has_value());
    assert(*bid == (mml::Level{9950, 100}));
}

void test_update_changes_existing_level_quantity() {
    mml::OrderBook book;

    book.apply_snapshot(
        {
            {10000, 250},
        },
        {
            {10050, 300},
        }
    );

    book.apply_update(mml::Side::Bid, {10000, 125});

    const auto bid = book.best_bid();

    assert(bid.has_value());
    assert(*bid == (mml::Level{10000, 125}));
}

void test_top_levels_are_sorted() {
    mml::OrderBook book;

    book.apply_snapshot(
        {
            {9900, 10},
            {10100, 30},
            {10000, 20},
        },
        {
            {10300, 10},
            {10200, 20},
            {10400, 30},
        }
    );

    const auto bids = book.top_bids(2);
    const auto asks = book.top_asks(2);

    assert((bids == std::vector<mml::Level>{{10100, 30}, {10000, 20}}));
    assert((asks == std::vector<mml::Level>{{10200, 20}, {10300, 10}}));
}

void test_validation_detects_missing_side() {
    mml::OrderBook book;

    book.apply_snapshot(
        {
            {10000, 250},
        },
        {}
    );

    const auto errors = book.validation_errors();

    assert(errors.size() == 1);
    assert(errors[0] == "missing asks");
    assert(!book.is_valid());
}

void test_validation_detects_crossed_book() {
    mml::OrderBook book;

    book.apply_snapshot(
        {
            {10100, 250},
        },
        {
            {10050, 300},
        }
    );

    const auto errors = book.validation_errors();

    assert(errors.size() == 1);
    assert(errors[0] == "crossed book");
    assert(!book.is_valid());
}

void test_rejects_non_positive_price() {
    mml::OrderBook book;
    bool threw = false;

    try {
        book.apply_snapshot(
            {
                {0, 100},
            },
            {
                {10050, 300},
            }
        );
    } catch (const std::invalid_argument&) {
        threw = true;
    }

    assert(threw);
}

void test_rejects_negative_quantity() {
    mml::OrderBook book;
    bool threw = false;

    try {
        book.apply_snapshot(
            {
                {10000, -1},
            },
            {
                {10050, 300},
            }
        );
    } catch (const std::invalid_argument&) {
        threw = true;
    }

    assert(threw);
}

}  // namespace

int main() {
    test_snapshot_sets_best_bid_and_ask();
    test_update_removes_best_bid();
    test_update_changes_existing_level_quantity();
    test_top_levels_are_sorted();
    test_validation_detects_missing_side();
    test_validation_detects_crossed_book();
    test_rejects_non_positive_price();
    test_rejects_negative_quantity();

    return 0;
}
