#include "mml/order_book.hpp"

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct Args {
    std::size_t events = 1'000'000;
    std::size_t depth = 10;
};

Args parse_args(int argc, char** argv) {
    Args args;

    for (int index = 1; index < argc; ++index) {
        const std::string option = argv[index];

        if (option == "--events" && index + 1 < argc) {
            args.events = static_cast<std::size_t>(std::strtoull(argv[++index], nullptr, 10));
        } else if (option == "--depth" && index + 1 < argc) {
            args.depth = static_cast<std::size_t>(std::strtoull(argv[++index], nullptr, 10));
        } else if (option == "--help") {
            std::cout << "usage: mml_replay_benchmark [--events N] [--depth N]\n";
            std::exit(0);
        } else {
            throw std::invalid_argument("unknown or incomplete option: " + option);
        }
    }

    if (args.events == 0) {
        throw std::invalid_argument("events must be positive");
    }

    if (args.depth == 0) {
        throw std::invalid_argument("depth must be positive");
    }

    return args;
}

std::vector<mml::Level> make_bids(std::size_t depth) {
    std::vector<mml::Level> levels;
    levels.reserve(depth);

    for (std::size_t index = 0; index < depth; ++index) {
        levels.push_back({100'000 - static_cast<std::int64_t>(index * 10), 1'000});
    }

    return levels;
}

std::vector<mml::Level> make_asks(std::size_t depth) {
    std::vector<mml::Level> levels;
    levels.reserve(depth);

    for (std::size_t index = 0; index < depth; ++index) {
        levels.push_back({100'010 + static_cast<std::int64_t>(index * 10), 1'000});
    }

    return levels;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const auto args = parse_args(argc, argv);

        mml::OrderBook book;
        book.apply_snapshot(make_bids(args.depth), make_asks(args.depth));

        const auto start = std::chrono::steady_clock::now();

        for (std::size_t index = 0; index < args.events; ++index) {
            const auto quantity = 1'000 + static_cast<std::int64_t>(index % 17);

            if (index % 2 == 0) {
                book.apply_update(mml::Side::Bid, {100'000, quantity});
            } else {
                book.apply_update(mml::Side::Ask, {100'010, quantity});
            }
        }

        const auto finish = std::chrono::steady_clock::now();
        const auto elapsed_ns =
            std::chrono::duration_cast<std::chrono::nanoseconds>(finish - start).count();
        const auto seconds = static_cast<double>(elapsed_ns) / 1'000'000'000.0;
        const auto events_per_second = static_cast<double>(args.events) / seconds;
        const auto ns_per_event = static_cast<double>(elapsed_ns) / static_cast<double>(args.events);

        std::cout << "{\n"
                  << "  \"events\": " << args.events << ",\n"
                  << "  \"depth\": " << args.depth << ",\n"
                  << "  \"elapsed_ns\": " << elapsed_ns << ",\n"
                  << "  \"events_per_second\": " << events_per_second << ",\n"
                  << "  \"ns_per_event\": " << ns_per_event << ",\n"
                  << "  \"bid_levels\": " << book.bid_level_count() << ",\n"
                  << "  \"ask_levels\": " << book.ask_level_count() << "\n"
                  << "}\n";
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
