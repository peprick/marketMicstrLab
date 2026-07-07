#include "mml/jsonl_replay.hpp"

#include <cassert>
#include <filesystem>
#include <fstream>
#include <vector>

namespace {

void test_decimal_to_fixed() {
    assert(mml::decimal_to_fixed("100.25", 100.0L) == 10025);
    assert(mml::decimal_to_fixed("5.1e-05", 100'000'000.0L) == 5100);
}

void test_parse_levels_from_json_line() {
    const std::string line =
        R"({"bids":[["100.00","3.0"],["99.50","1.25"]],"asks":[]})";

    const auto bids = mml::parse_levels_from_json_line(line, "bids", 100.0L);
    const auto asks = mml::parse_levels_from_json_line(line, "asks", 100.0L);

    assert((bids == std::vector<mml::Level>{{10000, 300}, {9950, 125}}));
    assert(asks.empty());
}

void test_replay_normalized_jsonl() {
    const auto path = std::filesystem::temp_directory_path() / "mml_cpp_replay_test.jsonl";

    {
        std::ofstream output(path);
        output << R"({"channel":"book","event_type":"snapshot","bids":[["100.00","3.0"],["99.50","1.0"]],"asks":[["100.50","1.0"]]})"
               << "\n";
        output << R"({"channel":"book","event_type":"update","bids":[["100.00","0"]],"asks":[["100.25","2.0"]]})"
               << "\n";
    }

    const auto stats = mml::replay_normalized_jsonl(path, 100.0L);

    assert(stats.events == 2);
    assert(stats.snapshots == 1);
    assert(stats.updates == 1);
    assert(stats.is_valid);
    assert(stats.best_bid.has_value());
    assert(stats.best_ask.has_value());
    assert(*stats.best_bid == (mml::Level{9950, 100}));
    assert(*stats.best_ask == (mml::Level{10025, 200}));

    std::filesystem::remove(path);
}

}  // namespace

int main() {
    test_decimal_to_fixed();
    test_parse_levels_from_json_line();
    test_replay_normalized_jsonl();
    return 0;
}
