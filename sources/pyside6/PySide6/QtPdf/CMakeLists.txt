# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtPdf_SRC
${QtPdf_GEN_DIR}/qpdfbookmarkmodel_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfdocument_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfdocumentrenderoptions_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfpagerenderer_wrapper.cpp
${QtPdf_GEN_DIR}/qpdflink_wrapper.cpp
${QtPdf_GEN_DIR}/qpdflinkmodel_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfpagenavigator_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfsearchmodel_wrapper.cpp
${QtPdf_GEN_DIR}/qpdfselection_wrapper.cpp
# module is always needed
${QtPdf_GEN_DIR}/qtpdf_module_wrapper.cpp
)

set(QtPdf_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtNetwork_GEN_DIR}
)

set(QtPdf_deps
    QtCore
    QtGui
    QtNetwork
)

set(QtPdf_libraries
    Qt::Pdf
)

create_pyside_module(NAME QtPdf
                     INCLUDE_DIRS QtPdf_include_dirs
                     LIBRARIES QtPdf_libraries
                     DEPS QtPdf_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtPdf_SRC
                     TYPESYSTEM_NAME "${CMAKE_CURRENT_BINARY_DIR}/typesystem_pdf.xml")
