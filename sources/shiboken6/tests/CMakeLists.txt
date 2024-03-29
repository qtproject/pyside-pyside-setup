# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

cmake_minimum_required(VERSION 3.18)

if(BUILD_TESTS)
    find_package(Qt${QT_MAJOR_VERSION}Test 6.0 REQUIRED)
endif()

add_subdirectory(libminimal)
if(NOT DEFINED MINIMAL_TESTS)
    add_subdirectory(libsample)
    add_subdirectory(libsmart)
    add_subdirectory(libother)
endif()

shiboken_get_debug_level(debug_level)

if(WIN32 OR DEFINED AVOID_PROTECTED_HACK)
    message(STATUS "Tests will be generated avoiding the protected hack!")
    set(GENERATOR_EXTRA_FLAGS --avoid-protected-hack)
else()
    message(STATUS "Tests will be generated using the protected hack!")
    set(GENERATOR_EXTRA_FLAGS )
endif()
list(APPEND GENERATOR_EXTRA_FLAGS ${SHIBOKEN_GENERATOR_EXTRA_FLAGS} ${debug_level})

add_subdirectory(minimalbinding)
if(NOT DEFINED MINIMAL_TESTS)
    add_subdirectory(samplebinding)
    add_subdirectory(smartbinding)
    add_subdirectory(otherbinding)
endif()

if(DEFINED MINIMAL_TESTS)
    file(GLOB TEST_FILES minimalbinding/*_test.py)
else()
    file(GLOB TEST_FILES minimalbinding/*_test.py
                         samplebinding/*_test.py
                         otherbinding/*_test.py
                         smartbinding/*_test.py
                         shibokenmodule/*_test.py)
endif()
list(SORT TEST_FILES)

set(test_blacklist "")

if(SHIBOKEN_IS_CROSS_BUILD)
    # Python_EXECUTABLE will be empty when cross-building.
    message(WARNING
        "Running tests when cross-compiling is not supported because it would require running "
        "a target python interpreter which might have a different architecture than the host."
    )
else()
    find_package(
        Python
        ${USE_PYTHON_VERSION}
        REQUIRED
        COMPONENTS Interpreter Development
    )
endif()

if(NOT CTEST_TESTING_TIMEOUT)
    set(CTEST_TESTING_TIMEOUT 60)
endif()

get_filename_component(BUILD_DIR "${libminimal_BINARY_DIR}" DIRECTORY)
get_filename_component(BUILD_DIR "${BUILD_DIR}" DIRECTORY)
get_filename_component(BUILD_DIR "${BUILD_DIR}" DIRECTORY)
foreach(test_file ${TEST_FILES})
    string(REGEX MATCH "/([^/]+)(binding|module)/([^/]+)_test.py" tmp ${test_file})
    set(test_name "${CMAKE_MATCH_1}_${CMAKE_MATCH_3}")
    list(FIND test_blacklist ${test_name} expect_fail)
    add_test(${test_name} ${Python_EXECUTABLE} ${test_file})
    set_tests_properties(${test_name} PROPERTIES ENVIRONMENT "BUILD_DIR=${BUILD_DIR}")
    set_tests_properties(${test_name} PROPERTIES TIMEOUT ${CTEST_TESTING_TIMEOUT})
    if (${expect_fail} GREATER -1)
        set_tests_properties(${test_name} PROPERTIES WILL_FAIL TRUE)
    endif()
endforeach()

# dumpcodemodel depends on apiextractor which is not cross-built.
if(SHIBOKEN_BUILD_TOOLS)
    add_subdirectory(dumpcodemodel)
endif()

# FIXME Skipped until add an option to choose the generator
# add_subdirectory(test_generator)

if (NOT APIEXTRACTOR_DOCSTRINGS_DISABLED)
    add_subdirectory(qtxmltosphinxtest)
endif()
