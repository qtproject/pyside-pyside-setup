# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtUiTools)

set(QtUiTools_SRC
${QtUiTools_GEN_DIR}/quiloader_wrapper.cpp
# module is always needed
${QtUiTools_GEN_DIR}/qtuitools_module_wrapper.cpp
)

set(QtUiTools_glue_sources
    "${CMAKE_CURRENT_SOURCE_DIR}/glue/plugins.h"
)

set(QtUiTools_static_sources
    "${CMAKE_CURRENT_SOURCE_DIR}/glue/loaduitype.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/glue/loaduitype.cpp"
)

set(QtUiTools_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtWidgets_GEN_DIR}
)

set(QtUiTools_deps
    QtWidgets
)

set(QtUiTools_libraries
    uiplugin
    Qt::UiTools
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/QtUiTools_global.pre.h.in"
               "${CMAKE_CURRENT_BINARY_DIR}/QtUiTools_global.pre.h" @ONLY)

create_pyside_module(NAME QtUiTools
                     INCLUDE_DIRS QtUiTools_include_dirs
                     LIBRARIES QtUiTools_libraries
                     DEPS QtUiTools_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     STATIC_SOURCES QtUiTools_static_sources
                     SOURCES QtUiTools_SRC
                     GLUE_SOURCES QtUiTools_glue_sources)
