#include "mml/order_book.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
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
    std::size_t runs = 1;
};

struct RunResult {
    std::int64_t elapsed_ns = 0;
    double events_per_second = 0.0;
    double ns_per_event = 0.0;
    std::size_t bid_levels = 0;
    std::size_t ask_levels = 0;
};

Args parse_args(int argc, char** argv) {
    Args args;

    for (int index = 1; index < argc; ++index) {
        const std::string option = argv[index];

        if (option == "--events" && index + 1 < argc) {
            args.events = static_cast<std::size_t>(std::strtoull(argv[++index], nullptr, 10));
        } else if (option == "--depth" && index + 1 < argc) {
            args.depth = static_cast<std::size_t>(std::strtoull(argv[++index], nullptr, 10));
        } else if (option == "--runs" && index + 1 < argc) {
            args.runs = static_cast<std::size_t>(std::strtoull(argv[++index], nullptr, 10));
        } else if (option == "--help") {
            std::cout << "usage: mml_replay_benchmark [--events N] [--depth N] [--runs N]\n";
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

    if (args.runs == 0) {
        throw std::invalid_argument("runs must be positive");
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

double percentile(std::vector<double> values, double quantile) {
    if (values.empty()) {
        return 0.0;
    }

    std::sort(values.begin(), values.end());
    const auto position =
        static_cast<std::size_t>(std::ceil(quantile * static_cast<double>(values.size() - 1)));
    return values[position];
}

RunResult run_once(std::size_t events, std::size_t depth) {
    mml::OrderBook book;
    book.apply_snapshot(make_bids(depth), make_asks(depth));

    const auto start = std::chrono::steady_clock::now();

    for (std::size_t index = 0; index < events; ++index) {
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

    return {
        elapsed_ns,
        static_cast<double>(events) / seconds,
        static_cast<double>(elapsed_ns) / static_cast<double>(events),
        book.bid_level_count(),
        book.ask_level_count(),
    };
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const auto args = parse_args(argc, argv);

        std::vector<double> ns_per_event_values;
        ns_per_event_values.reserve(args.runs);

        std::int64_t total_elapsed_ns = 0;
        RunResult last_run;

        for (std::size_t run = 0; run < args.runs; ++run) {
            last_run = run_once(args.events, args.depth);
            total_elapsed_ns += last_run.elapsed_ns;
            ns_per_event_values.push_back(last_run.ns_per_event);
        }

        const auto total_events = args.events * args.runs;
        const auto total_seconds = static_cast<double>(total_elapsed_ns) / 1'000'000'000.0;
        const auto mean_events_per_second = static_cast<double>(total_events) / total_seconds;
        const auto mean_ns_per_event =
            static_cast<double>(total_elapsed_ns) / static_cast<double>(total_events);

        std::cout << "{\n"
                  << "  \"events\": " << args.events << ",\n"
                  << "  \"depth\": " << args.depth << ",\n"
                  << "  \"runs\": " << args.runs << ",\n"
                  << "  \"elapsed_ns_total\": " << total_elapsed_ns << ",\n"
                  << "  \"mean_events_per_second\": " << mean_events_per_second << ",\n"
                  << "  \"mean_ns_per_event\": " << mean_ns_per_event << ",\n"
                  << "  \"p50_ns_per_event\": " << percentile(ns_per_event_values, 0.50) << ",\n"
                  << "  \"p95_ns_per_event\": " << percentile(ns_per_event_values, 0.95) << ",\n"
                  << "  \"p99_ns_per_event\": " << percentile(ns_per_event_values, 0.99) << ",\n"
                  << "  \"bid_levels\": " << last_run.bid_levels << ",\n"
                  << "  \"ask_levels\": " << last_run.ask_levels << "\n"
                  << "}\n";
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
