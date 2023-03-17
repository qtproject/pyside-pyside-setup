# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

cmake_minimum_required(VERSION 3.18)
cmake_policy(VERSION 3.18)

project(QtExampleIcons)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_AUTORCC ON)

set(CMAKE_AUTOMOC ON)

find_package(Qt6 COMPONENTS ExampleIconsPrivate)

add_library(QtExampleIcons MODULE module.c)

# See libshiboken/CMakeLists.txt
if(PYTHON_LIMITED_API)
    target_compile_definitions(QtExampleIcons PRIVATE "-DPy_LIMITED_API=0x03050000")
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(PYTHON_WITH_DEBUG)
        target_compile_definitions(QtExampleIcons PRIVATE "-DPy_DEBUG")
    endif()
    if (PYTHON_WITH_COUNT_ALLOCS)
        target_compile_definitions(QtExampleIcons PRIVATE "-DCOUNT_ALLOCS")
    endif()
elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_definitions(QtExampleIcons PRIVATE "-DNDEBUG")
endif()

target_include_directories(QtExampleIcons PRIVATE ${SHIBOKEN_PYTHON_INCLUDE_DIRS})

get_property(SHIBOKEN_PYTHON_LIBRARIES GLOBAL PROPERTY shiboken_python_libraries)

target_link_libraries(QtExampleIcons PRIVATE
                      Qt::ExampleIconsPrivate
                      ${SHIBOKEN_PYTHON_LIBRARIES})

set_target_properties(QtExampleIcons PROPERTIES
                      PREFIX ""
                      OUTPUT_NAME "QtExampleIcons${SHIBOKEN_PYTHON_EXTENSION_SUFFIX}"
                      LIBRARY_OUTPUT_DIRECTORY "${pyside6_BINARY_DIR}")

if(WIN32)
    set_property(TARGET QtExampleIcons PROPERTY SUFFIX ".pyd")
endif()

install(TARGETS QtExampleIcons LIBRARY DESTINATION "${PYTHON_SITE_PACKAGES}/PySide6")
