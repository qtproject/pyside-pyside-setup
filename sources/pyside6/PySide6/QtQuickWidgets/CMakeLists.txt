# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set (QtQuickWidgets_DROPPED_ENTRIES)

set(QtQuickWidgets_SRC
${QtQuickWidgets_GEN_DIR}/qquickwidget_wrapper.cpp
# module is always needed
${QtQuickWidgets_GEN_DIR}/qtquickwidgets_module_wrapper.cpp
)

set(QtQuickWidgets_include_dirs
    ${QtGui_GEN_DIR}
    ${QtOpenGL_GEN_DIR}
    ${QtCore_GEN_DIR}
    ${QtWidgets_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtQuick_GEN_DIR}
    ${QtQml_GEN_DIR}
    ${QtQuickWidgets_GEN_DIR}
)

set(QtQuickWidgets_deps
    QtGui
    QtQml
    QtQuick
    QtWidgets
    QtNetwork
)

set(QtQuickWidgets_libraries
    Qt::QuickWidgets
)

check_qt_opengl("QuickWidgets" QtQuickWidgets_include_dirs QtQuickWidgets_deps
                QtQuickWidgets_DROPPED_ENTRIES)

create_pyside_module(NAME QtQuickWidgets
                     INCLUDE_DIRS QtQuickWidgets_include_dirs
                     LIBRARIES QtQuickWidgets_libraries
                     DEPS QtQuickWidgets_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtQuickWidgets_SRC
                     DROPPED_ENTRIES QtQuickWidgets_DROPPED_ENTRIES)
