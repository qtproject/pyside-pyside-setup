# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtWebEngineQuick)

set(QtWebEngineQuick_SRC
${QtWebEngineQuick_GEN_DIR}/qquickwebenginedownloadrequest_wrapper.cpp
${QtWebEngineQuick_GEN_DIR}/qquickwebengineprofile_wrapper.cpp
${QtWebEngineQuick_GEN_DIR}/qtwebenginequick_wrapper.cpp
# module is always needed
${QtWebEngineQuick_GEN_DIR}/qtwebenginequick_module_wrapper.cpp
)

set(QtWebEngineQuick_DROPPED_ENTRIES)

set(QtWebEngineQuick_include_dirs
                            ${QtWebEngineQuick_SOURCE_DIR}
                            ${QtWebEngineQuick_BINARY_DIR}
                            ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Widgets_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}PrintSupport_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Qml_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}WebChannel_INCLUDE_DIRS}
                            ${libpyside_SOURCE_DIR}
                            ${QtCore_GEN_DIR}
                            ${QtGui_GEN_DIR}
                            ${QtWidgets_GEN_DIR}
                            ${QtNetwork_GEN_DIR}
                            ${QtWebEngineCore_GEN_DIR}
                            ${QtPrintSupport_GEN_DIR}
                            ${QtQml_GEN_DIR}
                            ${QtWebChannel_GEN_DIR})


# Disable "QWebEngineExtensionManager *QQuickWebEngineProfile::extensionManager()"
get_property(QtWebEngineCore_enabled_features TARGET Qt${QT_MAJOR_VERSION}::WebEngineCore
             PROPERTY QT_ENABLED_PUBLIC_FEATURES)

if(NOT "webengine_extensions" IN_LIST QtWebEngineCore_enabled_features)
    list(APPEND QtWebEngineQuick_DROPPED_ENTRIES QWebEngineExtensionInfo QWebEngineExtensionManager)
endif()

set(QtWebEngineQuick_libraries pyside6
                               ${Qt${QT_MAJOR_VERSION}WebEngineQuick_LIBRARIES})

set(QtWebEngineQuick_deps QtQml QtWebEngineCore)

create_pyside_module(NAME QtWebEngineQuick
                     INCLUDE_DIRS QtWebEngineQuick_include_dirs
                     LIBRARIES QtWebEngineQuick_libraries
                     DEPS QtWebEngineQuick_deps
                     TYPESYSTEM_PATH QtWebEngineQuick_SOURCE_DIR
                     SOURCES QtWebEngineQuick_SRC
                     DROPPED_ENTRIES QtWebEngineQuick_DROPPED_ENTRIES)
