#include "mml/jsonl_replay.hpp"

#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

struct Args {
    std::string input;
    long double scale = 100'000'000.0L;
};

Args parse_args(int argc, char** argv) {
    Args args;

    for (int index = 1; index < argc; ++index) {
        const std::string option = argv[index];

        if (option == "--input" && index + 1 < argc) {
            args.input = argv[++index];
        } else if (option == "--scale" && index + 1 < argc) {
            args.scale = std::strtold(argv[++index], nullptr);
        } else if (option == "--help") {
            std::cout << "usage: mml_replay_jsonl --input PATH [--scale N]\n";
            std::exit(0);
        } else {
            throw std::invalid_argument("unknown or incomplete option: " + option);
        }
    }

    if (args.input.empty()) {
        throw std::invalid_argument("--input is required");
    }

    return args;
}

void print_level_json(const char* name, const std::optional<mml::Level>& level) {
    std::cout << "  \"" << name << "\": ";
    if (!level.has_value()) {
        std::cout << "null";
        return;
    }

    std::cout << "{\"price\": " << level->price << ", \"quantity\": " << level->quantity << "}";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const auto args = parse_args(argc, argv);
        const auto stats = mml::replay_normalized_jsonl(args.input, args.scale);

        std::cout << "{\n"
                  << "  \"events\": " << stats.events << ",\n"
                  << "  \"snapshots\": " << stats.snapshots << ",\n"
                  << "  \"updates\": " << stats.updates << ",\n"
                  << "  \"is_valid\": " << (stats.is_valid ? "true" : "false") << ",\n";
        print_level_json("best_bid", stats.best_bid);
        std::cout << ",\n";
        print_level_json("best_ask", stats.best_ask);
        std::cout << "\n}\n";
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
