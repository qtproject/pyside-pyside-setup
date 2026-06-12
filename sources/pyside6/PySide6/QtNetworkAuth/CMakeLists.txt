# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtNetworkAuth_SRC
${QtNetworkAuth_GEN_DIR}/qabstractoauth_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qabstractoauth2_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qabstractoauthreplyhandler_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauth1_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauth1signature_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauth2authorizationcodeflow_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauth2deviceauthorizationflow_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauthhttpserverreplyhandler_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauthoobreplyhandler_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauthurischemereplyhandler_wrapper.cpp
# module is always needed
${QtNetworkAuth_GEN_DIR}/qtnetworkauth_module_wrapper.cpp
)

set(QtNetworkAuth_include_dirs
    ${QtCore_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtNetworkAuth_GEN_DIR}
)

set(QtNetworkAuth_deps
    QtNetwork
)

set(QtNetworkAuth_libraries
    Qt::NetworkAuth
)

create_pyside_module(NAME QtNetworkAuth
                     INCLUDE_DIRS QtNetworkAuth_include_dirs
                     LIBRARIES QtNetworkAuth_libraries
                     DEPS QtNetworkAuth_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtNetworkAuth_SRC)
