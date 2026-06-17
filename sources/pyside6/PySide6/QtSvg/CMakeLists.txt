# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtSvg)

set(QtSvg_SRC
${QtSvg_GEN_DIR}/qsvggenerator_wrapper.cpp
${QtSvg_GEN_DIR}/qsvgrenderer_wrapper.cpp
${QtSvg_GEN_DIR}/qtsvg_wrapper.cpp
# module is always needed
${QtSvg_GEN_DIR}/qtsvg_module_wrapper.cpp
)

set(QtSvg_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
)

set(QtSvg_deps
    QtGui
)

set(QtSvg_libraries
    Qt::Svg
)

create_pyside_module(NAME QtSvg
                     INCLUDE_DIRS QtSvg_include_dirs
                     LIBRARIES QtSvg_libraries
                     DEPS QtSvg_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtSvg_SRC)
