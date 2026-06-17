# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtHelp)

set(QtHelp_SRC
${QtHelp_GEN_DIR}/qcompressedhelpinfo_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpcontentitem_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpcontentmodel_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpcontentwidget_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpglobal_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpengine_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpenginecore_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpfilterdata_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpfilterengine_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpfiltersettingswidget_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpindexmodel_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpindexwidget_wrapper.cpp
${QtHelp_GEN_DIR}/qhelplink_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpsearchengine_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpsearchenginecore_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpsearchquery_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpsearchquerywidget_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpsearchresult_wrapper.cpp
${QtHelp_GEN_DIR}/qhelpsearchresultwidget_wrapper.cpp
# module is always needed
${QtHelp_GEN_DIR}/qthelp_module_wrapper.cpp
)

configure_file("${QtHelp_SOURCE_DIR}/QtHelp_global.pre.h.in"
               "${QtHelp_BINARY_DIR}/QtHelp_global.pre.h" @ONLY)

set(QtHelp_include_dirs
    ${QtWidgets_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtCore_GEN_DIR}
)

set(QtHelp_deps
    QtWidgets
)

set(QtHelp_libraries
    Qt::Help
)

create_pyside_module(NAME QtHelp
                     INCLUDE_DIRS QtHelp_include_dirs
                     LIBRARIES QtHelp_libraries
                     DEPS QtHelp_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtHelp_SRC)
