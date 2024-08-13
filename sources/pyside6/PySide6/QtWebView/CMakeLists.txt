# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtWebView)

set(QtWebView_Src
${QtWebView_GEN_DIR}/qtwebview_wrapper.cpp
# module is always needed
${QtWebView_GEN_DIR}/qtwebview_module_wrapper.cpp
)

set(QtWebView_include_dirs ${QtWebView_SOURCE_DIR}
                           ${QtWebView_BINARY_DIR}
                           ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                           ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                           ${Qt${QT_MAJOR_VERSION}WebView_INCLUDE_DIRS}
                           ${libpyside_SOURCE_DIR}
                           ${QtGui_GEN_DIR}
                           ${QtCore_GEN_DIR}
                           ${QtWebView_GEN_DIR})

set(QtWebView_libraries pyside6
                        ${Qt${QT_MAJOR_VERSION}WebView_LIBRARIES})

set(QtWebView_deps QtGui)

# for Windows and Linux, QtWebView depends on QtWebEngine to render content
if ((WIN32 OR UNIX) AND NOT APPLE)
    list(APPEND QtWebView_deps QtWebEngineCore QtWebEngineQuick)
endif()

create_pyside_module(NAME QtWebView
                     INCLUDE_DIRS QtWebView_include_dirs
                     LIBRARIES QtWebView_libraries
                     DEPS QtWebView_deps
                     TYPESYSTEM_PATH QtWebView_SOURCE_DIR
                     SOURCES QtWebView_Src)
