#include "mml/version.hpp"

#include <cassert>

int main() {
    assert(mml::version() == "0.1.0");
    return 0;
}
