#include "mml/jsonl_replay.hpp"

#include <cmath>
#include <fstream>
#include <stdexcept>

namespace {

std::string make_key(std::string_view key) {
    return "\"" + std::string(key) + "\"";
}

std::string find_json_string(std::string_view line, std::string_view key) {
    const auto key_pos = line.find(make_key(key));
    if (key_pos == std::string_view::npos) {
        return {};
    }

    const auto colon_pos = line.find(':', key_pos);
    if (colon_pos == std::string_view::npos) {
        return {};
    }

    const auto start_quote = line.find('"', colon_pos + 1);
    if (start_quote == std::string_view::npos) {
        return {};
    }

    const auto end_quote = line.find('"', start_quote + 1);
    if (end_quote == std::string_view::npos) {
        return {};
    }

    return std::string(line.substr(start_quote + 1, end_quote - start_quote - 1));
}

std::string_view array_for_key(std::string_view line, std::string_view key) {
    const auto key_pos = line.find(make_key(key));
    if (key_pos == std::string_view::npos) {
        return {};
    }

    const auto array_start = line.find('[', key_pos);
    if (array_start == std::string_view::npos) {
        return {};
    }

    int depth = 0;
    bool in_string = false;
    bool escaped = false;

    for (std::size_t index = array_start; index < line.size(); ++index) {
        const char ch = line[index];

        if (in_string) {
            if (escaped) {
                escaped = false;
            } else if (ch == '\\') {
                escaped = true;
            } else if (ch == '"') {
                in_string = false;
            }
            continue;
        }

        if (ch == '"') {
            in_string = true;
        } else if (ch == '[') {
            ++depth;
        } else if (ch == ']') {
            --depth;
            if (depth == 0) {
                return line.substr(array_start, index - array_start + 1);
            }
        }
    }

    throw std::invalid_argument("unterminated array for key: " + std::string(key));
}

std::vector<std::string> quoted_tokens(std::string_view text) {
    std::vector<std::string> tokens;
    bool in_string = false;
    bool escaped = false;
    std::size_t token_start = 0;

    for (std::size_t index = 0; index < text.size(); ++index) {
        const char ch = text[index];

        if (!in_string) {
            if (ch == '"') {
                in_string = true;
                token_start = index + 1;
            }
            continue;
        }

        if (escaped) {
            escaped = false;
        } else if (ch == '\\') {
            escaped = true;
        } else if (ch == '"') {
            tokens.emplace_back(text.substr(token_start, index - token_start));
            in_string = false;
        }
    }

    return tokens;
}

}  // namespace

namespace mml {

std::int64_t decimal_to_fixed(std::string_view value, long double scale) {
    if (scale <= 0) {
        throw std::invalid_argument("scale must be positive");
    }

    const auto parsed = std::stold(std::string(value));
    return static_cast<std::int64_t>(std::llround(parsed * scale));
}

std::vector<Level> parse_levels_from_json_line(
    std::string_view line,
    std::string_view key,
    long double scale
) {
    const auto array = array_for_key(line, key);
    const auto tokens = quoted_tokens(array);

    if (tokens.size() % 2 != 0) {
        throw std::invalid_argument("level array has an odd number of quoted values");
    }

    std::vector<Level> levels;
    levels.reserve(tokens.size() / 2);

    for (std::size_t index = 0; index < tokens.size(); index += 2) {
        levels.push_back(
            Level{
                decimal_to_fixed(tokens[index], scale),
                decimal_to_fixed(tokens[index + 1], scale),
            }
        );
    }

    return levels;
}

ReplayStats replay_normalized_jsonl(const std::filesystem::path& path, long double scale) {
    std::ifstream input(path);
    if (!input) {
        throw std::invalid_argument("could not open input file: " + path.string());
    }

    OrderBook book;
    ReplayStats stats;
    std::string line;

    while (std::getline(input, line)) {
        if (line.empty()) {
            continue;
        }

        const auto event_type = find_json_string(line, "event_type");
        if (event_type.empty()) {
            continue;
        }

        const auto bids = parse_levels_from_json_line(line, "bids", scale);
        const auto asks = parse_levels_from_json_line(line, "asks", scale);

        if (event_type == "snapshot") {
            book.apply_snapshot(bids, asks);
            ++stats.snapshots;
        } else if (event_type == "update") {
            book.apply_updates(bids, asks);
            ++stats.updates;
        } else {
            continue;
        }

        ++stats.events;
    }

    stats.best_bid = book.best_bid();
    stats.best_ask = book.best_ask();
    stats.validation_errors = book.validation_errors();
    stats.is_valid = stats.validation_errors.empty();
    return stats;
}

}  // namespace mml
