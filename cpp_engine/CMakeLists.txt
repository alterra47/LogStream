cmake_minimum_required(VERSION 3.10)
project(LogStreamEngine)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

find_package(ZeroMQ REQUIRED)
find_package(nlohmann_json REQUIRED)

include_directories(include)

add_executable(engine src/main.cpp src/InvertedIndex.cpp)

target_link_libraries(engine libzmq nlohmann_json::nlohmann_json)
