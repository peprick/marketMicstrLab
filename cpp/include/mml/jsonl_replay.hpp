#pragma once

#include "mml/order_book.hpp"

#include <filesystem>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace mml {

struct ReplayStats {
    std::size_t events = 0;
    std::size_t snapshots = 0;
    std::size_t updates = 0;
    std::optional<Level> best_bid;
    std::optional<Level> best_ask;
    bool is_valid = false;
    std::vector<std::string> validation_errors;
};

std::int64_t decimal_to_fixed(std::string_view value, long double scale = 100'000'000.0L);

std::vector<Level> parse_levels_from_json_line(
    std::string_view line,
    std::string_view key,
    long double scale = 100'000'000.0L
);

ReplayStats replay_normalized_jsonl(
    const std::filesystem::path& path,
    long double scale = 100'000'000.0L
);

}  // namespace mml
