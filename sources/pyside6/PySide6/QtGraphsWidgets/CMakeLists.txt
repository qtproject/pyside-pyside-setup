# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set (QtGraphsWidgets_DROPPED_ENTRIES)

set(QtGraphsWidgets_SRC
${QtGraphsWidgets_GEN_DIR}/q3dbarswidgetitem_wrapper.cpp
${QtGraphsWidgets_GEN_DIR}/q3dgraphswidgetitem_wrapper.cpp
${QtGraphsWidgets_GEN_DIR}/q3dscatterwidgetitem_wrapper.cpp
${QtGraphsWidgets_GEN_DIR}/q3dsurfacewidgetitem_wrapper.cpp

# module is always needed
${QtGraphsWidgets_GEN_DIR}/qtgraphswidgets_module_wrapper.cpp
)

set(QtGraphsWidgets_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtWidgets_GEN_DIR}
    ${QtGraphs_GEN_DIR}
    ${QtQml_GEN_DIR}
    ${QtQuick_GEN_DIR}
    ${QtQuickWidgets_GEN_DIR}
)

set(QtGraphsWidgets_deps
    QtQuickWidgets
    QtGraphs
)

set(QtGraphsWidgets_libraries
    Qt::GraphsWidgets
)

check_qt_opengl("GraphsWidgets" QtGraphsWidgets_include_dirs QtGraphsWidgets_deps
                 QtGraphsWidgets_DROPPED_ENTRIES)

create_pyside_module(NAME QtGraphsWidgets
                     INCLUDE_DIRS QtGraphsWidgets_include_dirs
                     LIBRARIES QtGraphsWidgets_libraries
                     DEPS QtGraphsWidgets_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtGraphsWidgets_SRC
                     STATIC_SOURCES QtGraphsWidgets_src
                     DROPPED_ENTRIES QtGraphsWidgets_DROPPED_ENTRIES)
