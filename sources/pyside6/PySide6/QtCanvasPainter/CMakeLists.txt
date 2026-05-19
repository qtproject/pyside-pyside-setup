# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtCanvasPainter)

set (QtCanvasPainter_DROPPED_ENTRIES)

set(QtCanvasPainter_SRC
${QtCanvasPainter_GEN_DIR}/qcanvasboxgradient_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasboxshadow_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasbrush_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasconicalgradient_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvascustombrush_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasgradient_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasgradientstop_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasgridpattern_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasimage_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasimagepattern_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvaslineargradient_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasoffscreencanvas_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvaspainter_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvaspainterfactory_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvaspainteritem_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvaspainteritemrenderer_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvaspath_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvaspainterwidget_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasradialgradient_wrapper.cpp
${QtCanvasPainter_GEN_DIR}/qcanvasrhipaintdriver_wrapper.cpp
# module is always needed
${QtCanvasPainter_GEN_DIR}/qtcanvaspainter_module_wrapper.cpp
)

set(QtGui_private_include_dirs
    ${Qt${QT_MAJOR_VERSION}Core_PRIVATE_INCLUDE_DIRS}
    ${Qt${QT_MAJOR_VERSION}Gui_PRIVATE_INCLUDE_DIRS})

configure_file("${QtCanvasPainter_SOURCE_DIR}/QtCanvasPainter_global.post.h.in"
               "${QtCanvasPainter_BINARY_DIR}/QtCanvasPainter_global.post.h" @ONLY)

set(QtCanvasPainter_include_dirs ${QtCanvasPainter_SOURCE_DIR}
                                  ${QtQml_SOURCE_DIR}
                                  ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                                  ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                                  ${QtGui_private_include_dirs}
                                  ${Qt${QT_MAJOR_VERSION}Widgets_INCLUDE_DIRS}
                                  ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                                  ${Qt${QT_MAJOR_VERSION}Qml_INCLUDE_DIRS}
                                  ${Qt${QT_MAJOR_VERSION}Quick_INCLUDE_DIRS}
                                  ${Qt${QT_MAJOR_VERSION}CanvasPainter_INCLUDE_DIRS}
                                  ${libpyside_SOURCE_DIR}
                                  ${QtWidgets_GEN_DIR}
                                  ${QtGui_GEN_DIR}
                                  ${QtCore_GEN_DIR}
                                  ${QtNetwork_GEN_DIR}
                                  ${QtQml_GEN_DIR}
                                  ${QtQuick_GEN_DIR}
                                  ${QtCanvasPainter_GEN_DIR})

set(QtCanvasPainter_libraries pyside6
    ${Qt${QT_MAJOR_VERSION}CanvasPainter_LIBRARIES})

set(QtCanvasPainter_deps QtGui QtWidgets QtNetwork QtQml QtQuick)

check_qt_opengl("CanvasPainter" QtCanvasPainter_include_dirs QtCanvasPainter_deps
                QtCanvasPainter_DROPPED_ENTRIES)

create_pyside_module(NAME QtCanvasPainter
                     INCLUDE_DIRS QtCanvasPainter_include_dirs
                     LIBRARIES QtCanvasPainter_libraries
                     DEPS QtCanvasPainter_deps
                     TYPESYSTEM_PATH QtCanvasPainter_SOURCE_DIR
                     SOURCES QtCanvasPainter_SRC
                     DROPPED_ENTRIES QtCanvasPainter_DROPPED_ENTRIES
                     ADDITIONAL_INCLUDE_DIRS QtGui_private_include_dirs)
