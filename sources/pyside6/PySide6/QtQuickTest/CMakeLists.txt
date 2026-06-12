# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set (QtQuickTest_DROPPED_ENTRIES)

set(QtQuickTest_SRC
# module is always needed
${QtQuickTest_GEN_DIR}/qtquicktest_module_wrapper.cpp
)

set(QtQuickTest_include_dirs
    ${QtGui_GEN_DIR}
    ${QtOpenGL_GEN_DIR}
    ${QtCore_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtQml_GEN_DIR}
    ${QtQuick_GEN_DIR}
    ${QtQuickTest_GEN_DIR}
)

set(QtQuickTest_deps
    QtGui
    QtNetwork
    QtQml
    QtQuick
)

set(QtQuickTest_libraries
    Qt::QuickTest
)

check_qt_opengl("QuickTest" QtQuickTest_include_dirs QtQuickTest_deps
                QtQuickTest_DROPPED_ENTRIES)

create_pyside_module(NAME QtQuickTest
                     INCLUDE_DIRS QtQuickTest_include_dirs
                     LIBRARIES QtQuickTest_libraries
                     DEPS QtQuickTest_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtQuickTest_SRC
                     DROPPED_ENTRIES QtQuickTest_DROPPED_ENTRIES)
