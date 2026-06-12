# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtHttpServer_SRC
    ${QtHttpServer_GEN_DIR}/qabstracthttpserver_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverconfiguration_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qfuturehttpserverresponse_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserver_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverresponder_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverrequest_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverresponse_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverrouter_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverrouterrule_wrapper.cpp
    ${QtHttpServer_GEN_DIR}/qhttpserverwebsocketupgraderesponse_wrapper.cpp
# module is always needed
    ${QtHttpServer_GEN_DIR}/qthttpserver_module_wrapper.cpp)

set(QtHttpServer_include_dirs
    ${QtCore_GEN_DIR}
    ${QtConcurrent_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtWebSockets_GEN_DIR}
)

set(QtHttpServer_deps QtCore QtConcurrent QtNetwork QtWebSockets)

set(QtHttpServer_libraries
    Qt::Concurrent
    Qt::HttpServer
)

create_pyside_module(NAME QtHttpServer
                     INCLUDE_DIRS QtHttpServer_include_dirs
                     LIBRARIES QtHttpServer_libraries
                     DEPS QtHttpServer_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtHttpServer_SRC)
