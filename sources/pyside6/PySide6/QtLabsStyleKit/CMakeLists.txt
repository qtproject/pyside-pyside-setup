# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtLabsStyleKit_SRC
${QtLabsStyleKit_GEN_DIR}/qstylekitstyle_wrapper.cpp
# module is always needed
${QtLabsStyleKit_GEN_DIR}/qtlabsstylekit_module_wrapper.cpp
)

set(QtLabsStyleKit_include_dirs ${QtCore_GEN_DIR}
                                ${QtGui_GEN_DIR}
                                ${QtWidgets_GEN_DIR})

set(QtLabsStyleKit_libraries Qt::LabsStyleKit)

set(QtLabsStyleKit_deps QtWidgets)

create_pyside_module(NAME QtLabsStyleKit
                     INCLUDE_DIRS QtLabsStyleKit_include_dirs
                     LIBRARIES QtLabsStyleKit_libraries
                     DEPS QtLabsStyleKit_deps
                     TYPESYSTEM_PATH QtLabsStyleKit_SOURCE_DIR
                     SOURCES QtLabsStyleKit_SRC
                     TYPESYSTEM_NAME ${QtLabsStyleKit_BINARY_DIR}/typesystem_labsstylekit.xml)
