# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtWebSockets_SRC
${QtWebSockets_GEN_DIR}/qmaskgenerator_wrapper.cpp
${QtWebSockets_GEN_DIR}/qwebsocket_wrapper.cpp
${QtWebSockets_GEN_DIR}/qwebsocketcorsauthenticator_wrapper.cpp
${QtWebSockets_GEN_DIR}/qwebsockethandshakeoptions_wrapper.cpp
${QtWebSockets_GEN_DIR}/qwebsocketprotocol_wrapper.cpp
${QtWebSockets_GEN_DIR}/qwebsocketserver_wrapper.cpp
# module is always needed
${QtWebSockets_GEN_DIR}/qtwebsockets_module_wrapper.cpp
)

set(QtWebSockets_include_dirs
    ${QtCore_GEN_DIR}
    ${QtWebSockets_GEN_DIR}
    ${QtNetwork_GEN_DIR}
)

set(QtWebSockets_deps
    QtNetwork
)

set(QtWebSockets_libraries
    Qt::WebSockets
)

create_pyside_module(NAME QtWebSockets
                     INCLUDE_DIRS QtWebSockets_include_dirs
                     LIBRARIES QtWebSockets_libraries
                     DEPS QtWebSockets_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtWebSockets_SRC)
