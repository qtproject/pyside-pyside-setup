include(cmake/Macros/icecc.cmake) # this must be the first line!

cmake_minimum_required(VERSION 3.16)
cmake_policy(VERSION 3.16)

project(pysidebindings)

include(cmake/PySideSetup.cmake)

add_subdirectory(libpyside)
find_package(Qt${QT_MAJOR_VERSION}Designer)
if(Qt${QT_MAJOR_VERSION}UiTools_FOUND AND Qt${QT_MAJOR_VERSION}Designer_FOUND)
    add_subdirectory(plugins/uitools)
    add_subdirectory(plugins/designer)
endif()

add_subdirectory(PySide6)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

add_subdirectory(doc)
