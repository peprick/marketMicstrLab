#include "mml/version.hpp"

#include <iostream>

int main() {
    std::cout << "Market Microstructure Lab " << mml::version() << '\n';
    return 0;
}
