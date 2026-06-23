# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtQmlFeatures)

add_library(QtQmlFeatures MODULE pyside_feature_module.cpp)

set_target_properties(QtQmlFeatures PROPERTIES
    PREFIX ""
    OUTPUT_NAME "QtQmlFeatures${SHIBOKEN_PYTHON_EXTENSION_SUFFIX}"
    LIBRARY_OUTPUT_DIRECTORY ${PYSIDE_PACKAGE_BINARY_DIR})

if(WIN32)
    set_target_properties(QtQmlFeatures PROPERTIES SUFFIX ".pyd")
endif()

target_link_libraries(QtQmlFeatures pyside6qml Shiboken6::libshiboken)

if(NOT (PYSIDE_IS_CROSS_BUILD OR DISABLE_PYI))
    pyside_setup_ld_prefix()

    set(generate_pyi_sys_path
        "${pysidebindings_BINARY_DIR}"
        "${PYTHON_SITE_PACKAGES}"
        "${PYTHON_SITE_PACKAGES}/../..")
    if(TARGET shibokenmodule)
        list(PREPEND generate_pyi_sys_path "$<TARGET_FILE_DIR:shibokenmodule>/..")
    endif()
    set(generate_pyi_options QtQmlFeatures --sys-path ${generate_pyi_sys_path})
    if(QUIET_BUILD)
        list(APPEND generate_pyi_options "--quiet")
    endif()

    add_custom_target(QtQmlFeatures_pyi ALL
                      COMMAND
                          ${CMAKE_COMMAND} -E env ${ld_prefix}
                          "${SHIBOKEN_PYTHON_INTERPRETER}"
                          "${CMAKE_CURRENT_SOURCE_DIR}/../support/generate_pyi.py"
                          ${generate_pyi_options})
    add_dependencies(QtQmlFeatures_pyi QtQmlFeatures)
    # QtQmlFeatures_pyi runs generate_pyi.py which imports PySide6.QtCore via
    # feature.__init__(). Add explicit dependencies so that the Python extension
    # modules are built before pyi generation starts
    if(TARGET QtCore)
        add_dependencies(QtQmlFeatures_pyi QtCore)
    endif()
    if(TARGET shibokenmodule)
        add_dependencies(QtQmlFeatures_pyi shibokenmodule)
    endif()

    install(FILES "${PYSIDE_PACKAGE_BINARY_DIR}/QtQmlFeatures.pyi"
            DESTINATION "${PYTHON_SITE_PACKAGES}/PySide6")
endif()

install(TARGETS QtQmlFeatures LIBRARY DESTINATION "${PYTHON_SITE_PACKAGES}/PySide6")
