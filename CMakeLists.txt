cmake_minimum_required(VERSION 3.20)

project(
    MarketMicrostructureLab
    VERSION 0.1.0
    DESCRIPTION "Order-book research and execution simulation lab"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(mml_core
    cpp/src/version.cpp
    cpp/src/order_book.cpp
)

target_include_directories(mml_core
    PUBLIC
        cpp/include
)

add_executable(mml_smoke
    cpp/tools/smoke.cpp
)

target_link_libraries(mml_smoke
    PRIVATE
        mml_core
)

add_executable(mml_replay_benchmark
    cpp/tools/benchmark_replay.cpp
)

target_link_libraries(mml_replay_benchmark
    PRIVATE
        mml_core
)

enable_testing()

add_executable(mml_core_tests
    cpp/tests/test_version.cpp
)

target_link_libraries(mml_core_tests
    PRIVATE
        mml_core
)

add_test(NAME mml_core_tests COMMAND mml_core_tests)


add_executable(mml_order_book_tests
    cpp/tests/test_order_book.cpp
)

target_link_libraries(mml_order_book_tests
    PRIVATE
        mml_core
)

add_test(NAME mml_order_book_tests COMMAND mml_order_book_tests)

add_test(
    NAME mml_replay_benchmark_smoke
    COMMAND mml_replay_benchmark --events 1000 --depth 10
)
