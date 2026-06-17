# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtQuickControls2)

set (QtQuickControls2_DROPPED_ENTRIES)

set(QtQuickControls2_SRC
${QtQuickControls2_GEN_DIR}/qquickstyle_wrapper.cpp
${QtQuickControls2_GEN_DIR}/qquickattachedpropertypropagator_wrapper.cpp
# module is always needed
${QtQuickControls2_GEN_DIR}/qtquickcontrols2_module_wrapper.cpp
)


set(QtQuickControls2_include_dirs
    ${QtGui_GEN_DIR}
    ${QtCore_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtQml_GEN_DIR}
    ${QtQuick_GEN_DIR}
    ${QtQuickControls2_GEN_DIR}
)

set(QtQuickControls2_deps
    QtGui
    QtNetwork
    QtQml
    QtQuick
)

set(QtQuickControls2_libraries
    Qt::QuickControls2
)

check_qt_opengl("QuickControls2" QtQuickControls2_include_dirs QtQuickControls2_deps
                QtQuickControls2_DROPPED_ENTRIES)

create_pyside_module(NAME QtQuickControls2
                     INCLUDE_DIRS QtQuickControls2_include_dirs
                     LIBRARIES QtQuickControls2_libraries
                     DEPS QtQuickControls2_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtQuickControls2_SRC
                     DROPPED_ENTRIES QtQuickControls2_DROPPED_ENTRIES)
