# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtWebChannel)

set(QtWebChannel_SRC
${QtWebChannel_GEN_DIR}/qwebchannel_wrapper.cpp
${QtWebChannel_GEN_DIR}/qwebchannelabstracttransport_wrapper.cpp
# module is always needed
${QtWebChannel_GEN_DIR}/qtwebchannel_module_wrapper.cpp
)

set(QtWebChannel_include_dirs
    ${QtCore_GEN_DIR}
)

set(QtWebChannel_deps
    QtCore
)

set(QtWebChannel_libraries
    Qt::WebChannel
)

create_pyside_module(NAME QtWebChannel
                     INCLUDE_DIRS QtWebChannel_include_dirs
                     LIBRARIES QtWebChannel_libraries
                     DEPS QtWebChannel_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtWebChannel_SRC)
