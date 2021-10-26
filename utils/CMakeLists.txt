cmake_minimum_required(VERSION 3.16)

project(utils)

find_package(PkgConfig REQUIRED)
pkg_check_modules(SDL2 REQUIRED sdl2)

add_executable(sdl-driver-test sdl-driver-test.cpp)
target_link_libraries(sdl-driver-test ${SDL2_LIBRARIES})
target_include_directories(sdl-driver-test PUBLIC ${SDL2_INCLUDE_DIRS})
target_compile_options(sdl-driver-test PUBLIC ${SDL2_CFLAGS_OTHER})

# add_executable(sdl-info-test sdl-info-test.c)