# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtPdfWidgets_SRC
${QtPdfWidgets_GEN_DIR}/qpdfpageselector_wrapper.cpp
${QtPdfWidgets_GEN_DIR}/qpdfview_wrapper.cpp
# module is always needed
${QtPdfWidgets_GEN_DIR}/qtpdfwidgets_module_wrapper.cpp
)

set(QtPdfWidgets_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtWidgets_GEN_DIR}
    ${QtPdf_GEN_DIR}
)

set(QtPdfWidgets_deps
    QtCore
    QtGui
    QtNetwork
    QtWidgets
    QtPdf
)

set(QtPdfWidgets_libraries
    Qt::PdfWidgets
)

create_pyside_module(NAME QtPdfWidgets
                     INCLUDE_DIRS QtPdfWidgets_include_dirs
                     LIBRARIES QtPdfWidgets_libraries
                     DEPS QtPdfWidgets_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtPdfWidgets_SRC
                     TYPESYSTEM_NAME "${CMAKE_CURRENT_BINARY_DIR}/typesystem_pdfwidgets.xml")
