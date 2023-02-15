# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtHttpServer)

set(QtHttpServer_SRC
    ${QtHttpServer_GEN_DIR}/qabstracthttpserver_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qfuturehttpserverresponse_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserver_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverresponder_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverrequest_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverresponse_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverrouter_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverrouterrule_wrapper.cpp
# module is always needed
    ${QtHttpServer_GEN_DIR}/qthttpserver_module_wrapper.cpp)

set(QtHttpServer_include_dirs ${QtHttpServer_SOURCE_DIR}
                                ${QtHttpServer_BINARY_DIR}
                                ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                                ${Qt${QT_MAJOR_VERSION}Concurrent_INCLUDE_DIRS}
                                ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                                ${Qt${QT_MAJOR_VERSION}WebSockets_INCLUDE_DIRS}
                                ${libpyside_SOURCE_DIR}
                                ${QtCore_GEN_DIR}
                                ${QtConcurrent_GEN_DIR}
                                ${QtNetwork_GEN_DIR}
                                ${QtWebSockets_GEN_DIR})

set(QtHttpServer_libraries pyside6
                           ${Qt${QT_MAJOR_VERSION}HttpServer_LIBRARIES}
                           ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                           ${Qt${QT_MAJOR_VERSION}Concurrent_LIBRARIES}
                           ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES}
                           ${Qt${QT_MAJOR_VERSION}WebSockets_LIBRARIES})

set(QtHttpServer_deps QtCore QtConcurrent QtNetwork QtWebSockets)

create_pyside_module(NAME QtHttpServer
                     INCLUDE_DIRS QtHttpServer_include_dirs
                     LIBRARIES QtHttpServer_libraries
                     DEPS QtHttpServer_deps
                     TYPESYSTEM_PATH QtHttpServer_SOURCE_DIR
                     SOURCES QtHttpServer_SRC)
