# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

include(cmake/Macros/icecc.cmake) # this must be the first line!

cmake_minimum_required(VERSION 3.18)
cmake_policy(VERSION 3.18)

include(".cmake.conf")
project(pysidebindings)

include(cmake/PySideSetup.cmake)

add_subdirectory(libpyside)

if(Qt${QT_MAJOR_VERSION}Qml_FOUND)
    add_subdirectory(libpysideqml)
endif()

if(Qt${QT_MAJOR_VERSION}UiTools_FOUND)
    add_subdirectory(plugins/uitools)
    find_package(Qt6 COMPONENTS Designer)
    # PYSIDE-535: Enable when PyPy supports embedding
    if (Qt${QT_MAJOR_VERSION}Designer_FOUND AND NOT PYPY_VERSION)
        add_subdirectory(plugins/designer)
    endif()
endif()

add_subdirectory(PySide6)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

add_subdirectory(doc)
