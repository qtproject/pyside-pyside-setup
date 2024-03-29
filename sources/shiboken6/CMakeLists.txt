# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

Include(icecc.cmake)

cmake_minimum_required(VERSION 3.18)
cmake_policy(VERSION 3.18)

set(CMAKE_BUILD_TYPE Release CACHE STRING "Build Type")

include(".cmake.conf")
project(shiboken6)
include(cmake/ShibokenSetup.cmake)

get_rpath_base_token(base)

set(CMAKE_INSTALL_RPATH ${base}/)

if(SHIBOKEN_BUILD_TOOLS)
    add_subdirectory(ApiExtractor) # Uses libclang
    add_subdirectory(generator) # Uses ApiExtractor And QtCore
endif()

if(SHIBOKEN_BUILD_LIBS)
    add_subdirectory(libshiboken) # Uses Python
    add_subdirectory(shibokenmodule) # Uses libshiboken
    add_subdirectory(data)
endif()

add_subdirectory(doc)

if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

