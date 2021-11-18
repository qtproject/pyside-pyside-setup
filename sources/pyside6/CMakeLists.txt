include(cmake/Macros/icecc.cmake) # this must be the first line!

cmake_minimum_required(VERSION 3.16)
cmake_policy(VERSION 3.16)

include(".cmake.conf")
project(pysidebindings)

include(cmake/PySideSetup.cmake)

add_subdirectory(libpyside)

if(Qt${QT_MAJOR_VERSION}Qml_FOUND)
    add_subdirectory(libpysideqml)
endif()

find_package(Qt${QT_MAJOR_VERSION}Designer)
if(Qt${QT_MAJOR_VERSION}UiTools_FOUND AND Qt${QT_MAJOR_VERSION}Designer_FOUND)
    add_subdirectory(plugins/uitools)
    # PYSIDE-535: Enable when PyPy supports embedding
    if (NOT PYPY_VERSION)
        add_subdirectory(plugins/designer)
    endif()
endif()

add_subdirectory(PySide6)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

add_subdirectory(doc)
