# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtSerialPort_OPTIONAL_SRC )
set(QtSerialPort_DROPPED_ENTRIES )

set(QtSerialPort_SRC
    ${QtSerialPort_GEN_DIR}/qserialport_wrapper.cpp
    ${QtSerialPort_GEN_DIR}/qserialportinfo_wrapper.cpp
# module is always needed
    ${QtSerialPort_GEN_DIR}/qtserialport_module_wrapper.cpp
)

set(QtSerialPort_include_dirs
    ${QtCore_GEN_DIR}
)

set(QtSerialPort_deps
    QtCore
)

set(QtSerialPort_libraries
    Qt::SerialPort
)

create_pyside_module(NAME QtSerialPort
                     INCLUDE_DIRS QtSerialPort_include_dirs
                     LIBRARIES QtSerialPort_libraries
                     DEPS QtSerialPort_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtSerialPort_SRC
                     DROPPED_ENTRIES QtSerialPort_DROPPED_ENTRIES)
