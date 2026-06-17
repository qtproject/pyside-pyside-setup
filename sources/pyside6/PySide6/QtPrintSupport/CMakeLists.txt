# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtPrintSupport)

set(QtPrintSupport_SRC
${QtPrintSupport_GEN_DIR}/qabstractprintdialog_wrapper.cpp
${QtPrintSupport_GEN_DIR}/qpagesetupdialog_wrapper.cpp
${QtPrintSupport_GEN_DIR}/qprintdialog_wrapper.cpp
${QtPrintSupport_GEN_DIR}/qprintengine_wrapper.cpp
${QtPrintSupport_GEN_DIR}/qprinter_wrapper.cpp
${QtPrintSupport_GEN_DIR}/qprinterinfo_wrapper.cpp
${QtPrintSupport_GEN_DIR}/qprintpreviewdialog_wrapper.cpp
${QtPrintSupport_GEN_DIR}/qprintpreviewwidget_wrapper.cpp
# module is always needed
${QtPrintSupport_GEN_DIR}/qtprintsupport_module_wrapper.cpp
)

set(QtPrintSupport_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtWidgets_GEN_DIR}
)

set(QtPrintSupport_deps
    QtWidgets
)

set(QtPrintSupport_libraries
    Qt::PrintSupport
)

create_pyside_module(NAME QtPrintSupport
                     INCLUDE_DIRS QtPrintSupport_include_dirs
                     LIBRARIES QtPrintSupport_libraries
                     DEPS QtPrintSupport_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtPrintSupport_SRC
                     TYPESYSTEM_NAME "${CMAKE_CURRENT_BINARY_DIR}/typesystem_printsupport.xml")
