# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtSvgWidgets)

set(QtSvgWidgets_SRC
${QtSvgWidgets_GEN_DIR}/qgraphicssvgitem_wrapper.cpp
${QtSvgWidgets_GEN_DIR}/qsvgwidget_wrapper.cpp
# module is always needed
${QtSvgWidgets_GEN_DIR}/qtsvgwidgets_module_wrapper.cpp
)

set(QtSvgWidgets_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtWidgets_GEN_DIR}
    ${QtSvg_GEN_DIR}
)

set(QtSvgWidgets_deps QtSvg QtWidgets)

set(QtSvgWidgets_libraries
    Qt::SvgWidgets
)

create_pyside_module(NAME QtSvgWidgets
                     INCLUDE_DIRS QtSvgWidgets_include_dirs
                     LIBRARIES QtSvgWidgets_libraries
                     DEPS QtSvgWidgets_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtSvgWidgets_SRC)
