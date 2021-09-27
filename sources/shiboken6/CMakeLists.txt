Include(icecc.cmake)

cmake_minimum_required(VERSION 3.16)
cmake_policy(VERSION 3.16)

set(CMAKE_BUILD_TYPE Release CACHE STRING "Build Type")

include(".cmake.conf")
project(shiboken6)

include(cmake/ShibokenSetup.cmake)

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

