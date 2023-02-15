# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtPdfWidgets)

set(QtPdfWidgets_SRC
${QtPdfWidgets_GEN_DIR}/qpdfview_wrapper.cpp
# module is always needed
${QtPdfWidgets_GEN_DIR}/qtpdfwidgets_module_wrapper.cpp
)

set(QtPdfWidgets_include_dirs ${QtPdfWidgets_SOURCE_DIR}
                              ${QtPdfWidgets_BINARY_DIR}
                              ${pyside6_SOURCE_DIR}
                              ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                              ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                              ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                              ${Qt${QT_MAJOR_VERSION}Widgets_INCLUDE_DIRS}
                              ${Qt${QT_MAJOR_VERSION}Pdf_INCLUDE_DIRS}
                              ${libpyside_SOURCE_DIR}
                              ${QtCore_GEN_DIR}
                              ${QtGui_GEN_DIR}
                              ${QtNetwork_GEN_DIR}
                              ${QtWidgets_GEN_DIR}
                              ${QtPdf_GEN_DIR})

set(QtPdfWidgets_libraries pyside6
    ${Qt${QT_MAJOR_VERSION}Pdf_LIBRARIES}
    ${Qt${QT_MAJOR_VERSION}PdfWidgets_LIBRARIES}
    ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
    ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
    ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES}
    ${Qt${QT_MAJOR_VERSION}Widgets_LIBRARIES})

set(QtPdfWidgets_deps QtCore QtGui QtNetwork QtWidgets QtPdf)

create_pyside_module(NAME QtPdfWidgets
                     INCLUDE_DIRS QtPdfWidgets_include_dirs
                     LIBRARIES QtPdfWidgets_libraries
                     DEPS QtPdfWidgets_deps
                     TYPESYSTEM_PATH QtPdfWidgets_SOURCE_DIR
                     SOURCES QtPdfWidgets_SRC
                     TYPESYSTEM_NAME ${QtPdfWidgets_BINARY_DIR}/typesystem_pdfwidgets.xml)
