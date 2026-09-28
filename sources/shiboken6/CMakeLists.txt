# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

Include(icecc.cmake)

cmake_minimum_required(VERSION 3.25)
cmake_policy(VERSION 3.22)

set(CMAKE_BUILD_TYPE Release CACHE STRING "Build Type")

include(".cmake.conf")
project(shiboken6)

include(cmake/ShibokenSetup.cmake)

get_rpath_base_token(base)

set(CMAKE_INSTALL_RPATH ${base}/)

add_subdirectory(libshiboken) # Uses Python
add_subdirectory(shibokenmodule) # Uses libshiboken
add_subdirectory(data)

if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
