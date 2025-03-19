# Copyright (C) 2025 Ford Motor Company
# SPDX-License-Identifier: BSD-3-Clause

if (NOT CMAKE_MINIMUM_REQUIRED_VERSION)
    cmake_minimum_required(VERSION 3.18)
    cmake_policy(VERSION 3.18)
endif()

project(libpysideremoteobjects LANGUAGES CXX)

if (NOT libpyside_SOURCE_DIR) # Building standalone
    message(STATUS "Building standalone. Setting C++ standard and build type.")
    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    if(NOT CMAKE_BUILD_TYPE)
        set(CMAKE_BUILD_TYPE Release)
    endif()
    find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
    find_package(Shiboken6 REQUIRED)
    find_package(libpyside REQUIRED)
    get_target_property(pyside6_SOURCE_DIR PySide6::pyside6 INTERFACE_INCLUDE_DIRECTORIES)
endif()

find_package(Qt6 REQUIRED COMPONENTS Core RepParser RemoteObjects RemoteObjectsPrivate)

set(libpysideremoteobjects_HEADERS
    pysidecapsulemethod_p.h
    pysidedynamicclass_p.h
    pysidedynamiccommon_p.h
    pysidedynamicenum_p.h
    pysidedynamicpod_p.h
    pysiderephandler_p.h
)

set(libpysideremoteobjects_SRC
    pysiderephandler.cpp
    pysidecapsulemethod.cpp
    pysidedynamiccommon.cpp
    pysidedynamicclass.cpp
    pysidedynamicpod.cpp
    pysidedynamicenum.cpp
    ${libpysideremoteobjects_HEADERS}
)

list(GET Qt6RepParser_INCLUDE_DIRS 0 REPPARSER_DIR)

include(QtTargetHelpers)
include(QtTestHelpers)
include(QtLalrHelpers)
add_library(pyside6remoteobjects STATIC ${libpysideremoteobjects_SRC})

target_include_directories(pyside6remoteobjects PRIVATE
    ${REPPARSER_DIR}
    ${Qt${QT_VERSION_MAJOR}Core_PRIVATE_INCLUDE_DIRS}
    ${Qt${QT_MAJOR_VERSION}RemoteObjects_INCLUDE_DIRS}
    ${Qt${QT_MAJOR_VERSION}RemoteObjects_PRIVATE_INCLUDE_DIRS}
    ${pyside6_SOURCE_DIR}                     # Added internally by the create_pyside_module function
    ${SHIBOKEN_INCLUDE_DIR}
    ${libpyside_SOURCE_DIR}
    ${SHIBOKEN_PYTHON_INCLUDE_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}               # Include the component-specific build directory
)

target_link_libraries(pyside6remoteobjects PRIVATE
    Shiboken6::libshiboken                    # Added internally by the create_pyside_module function
    Qt6::Core
    Qt6::RemoteObjectsPrivate
)

qt_process_qlalr(
    pyside6remoteobjects
    "${REPPARSER_DIR}/parser.g"
    ""
)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D QT_NO_CAST_FROM_ASCII -D QT_NO_CAST_TO_ASCII")

#
# install stuff
#

install(FILES ${libpysideremoteobjects_HEADERS}
        DESTINATION include/${BINDING_NAME}${pyside6remoteobjects_SUFFIX})

install(TARGETS pyside6remoteobjects EXPORT PySide6RemoteObjectsTargets
                           LIBRARY DESTINATION "${LIB_INSTALL_DIR}"
                           ARCHIVE DESTINATION "${LIB_INSTALL_DIR}"
                           RUNTIME DESTINATION bin)
