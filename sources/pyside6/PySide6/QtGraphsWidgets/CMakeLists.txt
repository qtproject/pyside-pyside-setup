# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtGraphsWidgets)

set(QtGraphsWidgets_SRC
${QtGraphsWidgets_GEN_DIR}/q3dbarswidgetitem_wrapper.cpp
${QtGraphsWidgets_GEN_DIR}/q3dgraphswidgetitem_wrapper.cpp
${QtGraphsWidgets_GEN_DIR}/q3dscatterwidgetitem_wrapper.cpp
${QtGraphsWidgets_GEN_DIR}/q3dsurfacewidgetitem_wrapper.cpp

# module is always needed
${QtGraphsWidgets_GEN_DIR}/qtgraphswidgets_module_wrapper.cpp
)

set(QtGraphsWidgets_include_dirs ${QtGraphsWidgets_SOURCE_DIR}
                                 ${QtGraphsWidgets_BINARY_DIR}
                                 ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                                 ${Qt${QT_MAJOR_VERSION}QtNetwork_INCLUDE_DIRS}
                                 ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                                 ${Qt${QT_MAJOR_VERSION}OpenGL_INCLUDE_DIRS}
                                 ${Qt${QT_MAJOR_VERSION}Widgets_INCLUDE_DIRS}
                                 ${Qt${QT_MAJOR_VERSION}Graphs_INCLUDE_DIRS}
                                 ${Qt${QT_MAJOR_VERSION}Qml_INCLUDE_DIRS}
                                 ${Qt${QT_MAJOR_VERSION}Quick_INCLUDE_DIRS}
                                 ${Qt${QT_MAJOR_VERSION}QuickWidgets_INCLUDE_DIRS}
                                 ${QtCore_GEN_DIR}
                                 ${QtGui_GEN_DIR}
                                 ${QtNetwork_GEN_DIR}
                                 ${QtOpenGL_GEN_DIR}
                                 ${QtWidgets_GEN_DIR}
                                 ${QtGraphs_GEN_DIR}
                                 ${QtQml_GEN_DIR}
                                 ${QtQuick_GEN_DIR}
                                 ${QtQuickWidgets_GEN_DIR}
                                 ${libpyside_SOURCE_DIR}
)

set(QtGraphsWidgets_libraries pyside6
    ${Qt${QT_MAJOR_VERSION}GraphsWidgets_LIBRARIES})

set(QtGraphsWidgets_deps QtQuickWidgets QtGraphs)

create_pyside_module(NAME QtGraphsWidgets
                     INCLUDE_DIRS QtGraphsWidgets_include_dirs
                     LIBRARIES QtGraphsWidgets_libraries
                     DEPS QtGraphsWidgets_deps
                     TYPESYSTEM_PATH QtGraphsWidgets_SOURCE_DIR
                     SOURCES QtGraphsWidgets_SRC
                     STATIC_SOURCES QtGraphsWidgets_src)
