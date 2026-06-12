# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtWebEngineWidgets_SRC
${QtWebEngineWidgets_GEN_DIR}/qwebengineview_wrapper.cpp
# module is always needed
${QtWebEngineWidgets_GEN_DIR}/qtwebenginewidgets_module_wrapper.cpp
)

set(QtWebEngineWidgets_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtWidgets_GEN_DIR}
    ${QtWebEngineWidgets_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtWebEngineCore_GEN_DIR}
    ${QtPrintSupport_GEN_DIR}
    ${QtWebChannel_GEN_DIR}
)

set(QtWebEngineWidgets_deps
    QtGui
    QtWidgets
    QtNetwork
    QtPrintSupport
    QtWebChannel
    QtWebEngineCore
)

set(QtWebEngineWidgets_libraries
    Qt::WebEngineWidgets
)

create_pyside_module(NAME QtWebEngineWidgets
                     INCLUDE_DIRS QtWebEngineWidgets_include_dirs
                     LIBRARIES QtWebEngineWidgets_libraries
                     DEPS QtWebEngineWidgets_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtWebEngineWidgets_SRC)
