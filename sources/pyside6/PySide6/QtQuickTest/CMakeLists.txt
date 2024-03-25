# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtQuickTest)

set (QtQuickTest_DROPPED_ENTRIES)

set(QtQuickTest_SRC
# module is always needed
${QtQuickTest_GEN_DIR}/qtquicktest_module_wrapper.cpp
)

set(QtQuickTest_include_dirs ${QtQuickTest_SOURCE_DIR}
                             ${QtQml_SOURCE_DIR}
                             ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                             ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                             ${Qt${QT_MAJOR_VERSION}OpenGL_INCLUDE_DIRS}
                             ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                             ${Qt${QT_MAJOR_VERSION}Qml_INCLUDE_DIRS}
                             ${Qt${QT_MAJOR_VERSION}Quick_INCLUDE_DIRS}
                             ${libpyside_SOURCE_DIR}
                             ${QtGui_GEN_DIR}
                             ${QtOpenGL_GEN_DIR}
                             ${QtCore_GEN_DIR}
                             ${QtNetwork_GEN_DIR}
                             ${QtQml_GEN_DIR}
                             ${QtQuick_GEN_DIR}
                             ${QtQuickTest_GEN_DIR})

set(QtQuickTest_libraries pyside6
                          ${Qt${QT_MAJOR_VERSION}QuickTest_LIBRARIES})

set(QtQuickTest_deps QtGui QtNetwork QtQml QtQuick)

check_qt_opengl("QuickTest" QtQuickTest_include_dirs QtQuickTest_deps
                QtQuickTest_DROPPED_ENTRIES)

create_pyside_module(NAME QtQuickTest
                     INCLUDE_DIRS QtQuickTest_include_dirs
                     LIBRARIES QtQuickTest_libraries
                     DEPS QtQuickTest_deps
                     TYPESYSTEM_PATH QtQuickTest_SOURCE_DIR
                     SOURCES QtQuickTest_SRC
                     DROPPED_ENTRIES QtQuickTest_DROPPED_ENTRIES)
