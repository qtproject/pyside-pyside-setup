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

# Ensure Shiboken6 and Shiboken6Tools packags are found during super-build
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_BINARY_DIR}/sources/shiboken6/data")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_BINARY_DIR}/sources/shiboken6/generator")
add_subdirectory(sources/pyside6)

add_subdirectory(sources/pyside-tools)

# Ensure PySide package is found during super-build
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_BINARY_DIR}/sources/pyside6/libpyside")
