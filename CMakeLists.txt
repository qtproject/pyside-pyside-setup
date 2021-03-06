cmake_minimum_required(VERSION 3.16)
cmake_policy(VERSION 3.16)

set(CMAKE_BUILD_TYPE Release CACHE STRING "Build Type")

project(pyside6_super_project)

if (CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR "In-source builds are not allowed.")
endif()

# Used to prevent overriding message function in both shiboken6 and pyside6.
set(is_pyside6_superproject_build 1)

add_subdirectory(sources/shiboken6)

# Semi-hack to include exported shiboken variables.
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_BINARY_DIR}/sources/shiboken6/data")
add_subdirectory(sources/pyside6)

add_subdirectory(sources/pyside-tools)

# Semi-hack to include exported pyside6 variables.
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_BINARY_DIR}/sources/pyside6/libpyside")
