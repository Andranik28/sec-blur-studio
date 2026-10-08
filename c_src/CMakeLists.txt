cmake_minimum_required(VERSION 3.10)
project(SecBlurStudio VERSION 1.0 LANGUAGES CXX)

# Use C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenCV library
find_package(OpenCV REQUIRED)

# Include directories
include_directories(include ${OpenCV_INCLUDE_DIRS})

# Create the main executable
add_executable(secblur_cli src/main.cpp src/secblur.cpp)

# Link OpenCV libraries to the executable
target_link_libraries(secblur_cli ${OpenCV_LIBS})
