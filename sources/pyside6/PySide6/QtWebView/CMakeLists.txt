# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtWebView_Src
${QtWebView_GEN_DIR}/qtwebview_wrapper.cpp
${QtWebView_GEN_DIR}/qwebview_wrapper.cpp
${QtWebView_GEN_DIR}/qwebviewloadinginfo_wrapper.cpp
${QtWebView_GEN_DIR}/qwebviewsettings_wrapper.cpp
# module is always needed
${QtWebView_GEN_DIR}/qtwebview_module_wrapper.cpp
)

set(QtWebView_include_dirs
    ${QtGui_GEN_DIR}
    ${QtCore_GEN_DIR}
    ${QtWebView_GEN_DIR}
)

set(QtWebView_libraries
    Qt::WebView
)

set(QtWebView_deps
    QtGui
)

# for Windows and Linux, QtWebView depends on QtWebEngine to render content
# On Android, QtWebView uses the native webview backend and does not require QtWebEngine.
if ((WIN32 OR UNIX) AND NOT APPLE AND NOT ANDROID)
    list(APPEND QtWebView_deps QtWebEngineCore QtWebEngineQuick)
endif()

create_pyside_module(NAME QtWebView
                     INCLUDE_DIRS QtWebView_include_dirs
                     LIBRARIES QtWebView_libraries
                     DEPS QtWebView_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtWebView_Src)
