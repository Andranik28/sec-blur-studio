cmake_minimum_required(VERSION 3.14)
project(sec_blur_studio VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCV REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(ZLIB REQUIRED)

include_directories(${OpenCV_INCLUDE_DIRS} ${OPENSSL_INCLUDE_DIR} ${ZLIB_INCLUDE_DIRS} cpp/include)

add_executable(secblur cpp/src/main.cpp cpp/src/secblur.cpp)

target_link_libraries(secblur 
    PRIVATE 
    ${OpenCV_LIBS} 
    OpenSSL::Crypto 
    ZLIB::ZLIB
)
