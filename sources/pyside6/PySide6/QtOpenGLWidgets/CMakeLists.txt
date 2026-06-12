# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtOpenGLWidgets_SRC
${QtOpenGLWidgets_GEN_DIR}/qopenglwidget_wrapper.cpp
# module is always needed
${QtOpenGLWidgets_GEN_DIR}/qtopenglwidgets_module_wrapper.cpp
)

set(QtOpenGLWidgets_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtWidgets_GEN_DIR}
    ${QtOpenGLWidgets_GEN_DIR}
)

set(QtOpenGLWidgets_deps QtOpenGL QtWidgets)

set(QtOpenGLWidgets_libraries
    Qt::OpenGLWidgets
)

create_pyside_module(NAME QtOpenGLWidgets
                     INCLUDE_DIRS QtOpenGLWidgets_include_dirs
                     LIBRARIES QtOpenGLWidgets_libraries
                     DEPS QtOpenGLWidgets_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtOpenGLWidgets_SRC)
