include(cmake/Macros/icecc.cmake) # this must be the first line!

cmake_minimum_required(VERSION 3.16)
cmake_policy(VERSION 3.16)

project(pysidebindings)

include(cmake/PySideSetup.cmake)

add_subdirectory(libpyside)
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

if(QT_SRC_DIR AND SPHINX_BUILD AND DOT_EXEC AND NOT SKIP_DOCS)
    add_subdirectory(doc)
else()
    set(DOCS_TARGET_DISABLED_MESSAGE "apidoc generation targets disabled.")
    if(NOT QT_SRC_DIR)
        message(STATUS "QT_SRC_DIR variable not set, ${DOCS_TARGET_DISABLED_MESSAGE}")
    elseif(NOT SPHINX_BUILD)
        message(STATUS "sphinx-build command not found, ${DOCS_TARGET_DISABLED_MESSAGE}")
    elseif(NOT DOT_EXEC)
        message(STATUS "graphviz not found, ${DOCS_TARGET_DISABLED_MESSAGE}")
    else()
        message(STATUS "Unknown issue occurred, ${DOCS_TARGET_DISABLED_MESSAGE}")
    endif()
endif()
