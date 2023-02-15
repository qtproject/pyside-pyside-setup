# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtPdf)

set(QtPdf_SRC
${QtPdf_GEN_DIR}/qpdfbookmarkmodel_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfdocument_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfdocumentrenderoptions_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfpagerenderer_wrapper.cpp
${QtPdf_GEN_DIR}/qpdflink_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfpagenavigator_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfsearchmodel_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfselection_wrapper.cpp
# module is always needed
${QtPdf_GEN_DIR}/qtpdf_module_wrapper.cpp
)

set(QtPdf_include_dirs ${QtPdf_SOURCE_DIR}
                       ${QtPdf_BINARY_DIR}
                       ${pyside6_SOURCE_DIR}
                       ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                       ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                       ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                       ${libpyside_SOURCE_DIR}
                       ${QtCore_GEN_DIR}
                       ${QtGui_GEN_DIR}
                       ${QtNetwork_GEN_DIR})

set(QtPdf_libraries pyside6
    ${Qt${QT_MAJOR_VERSION}Pdf_LIBRARIES}
    ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
    ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
    ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES})

set(QtPdf_deps QtCore QtGui QtNetwork)

create_pyside_module(NAME QtPdf
                     INCLUDE_DIRS QtPdf_include_dirs
                     LIBRARIES QtPdf_libraries
                     DEPS QtPdf_deps
                     TYPESYSTEM_PATH QtPdf_SOURCE_DIR
                     SOURCES QtPdf_SRC
                     TYPESYSTEM_NAME ${QtPdf_BINARY_DIR}/typesystem_pdf.xml)
