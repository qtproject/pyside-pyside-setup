# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtSerialBus)

set(QtSerialBus_OPTIONAL_SRC )
set(QtSerialBus_DROPPED_ENTRIES )

set(QtSerialBus_SRC
    ${QtSerialBus_GEN_DIR}/qcanbus_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qcanbusdevice_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qcanbusdevice_filter_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qcanbusdeviceinfo_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qcanbusfactory_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qcanbusframe_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qcanbusframe_timestamp_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusclient_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusdataunit_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusdevice_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusdeviceidentification_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbuspdu_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusreply_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusrequest_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusrtuserialclient_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusrtuserialserver_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbusserver_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbustcpclient_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbustcpconnectionobserver_wrapper.cpp
    ${QtSerialBus_GEN_DIR}/qmodbustcpserver_wrapper.cpp
# module is always needed
    ${QtSerialBus_GEN_DIR}/qtserialbus_module_wrapper.cpp
)

set(QtSerialBus_include_dirs ${QtSerialBus_SOURCE_DIR}
                              ${QtSerialBus_BINARY_DIR}
                              ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                              ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                              ${Qt${QT_MAJOR_VERSION}SerialPort_INCLUDE_DIRS}
                              ${Qt${QT_MAJOR_VERSION}SerialBus_INCLUDE_DIRS}
                              ${libpyside_SOURCE_DIR}
                              ${QtCore_GEN_DIR}
                              ${QtNetwork_GEN_DIR}
                              ${QtSerialPort_GEN_DIR})

set(QtSerialBus_libraries pyside6
    ${Qt${QT_MAJOR_VERSION}SerialBus_LIBRARIES})

set(QtSerialBus_deps QtCore QtNetwork QtSerialPort)

create_pyside_module(NAME QtSerialBus
                     INCLUDE_DIRS QtSerialBus_include_dirs
                     LIBRARIES QtSerialBus_libraries
                     DEPS QtSerialBus_deps
                     TYPESYSTEM_PATH QtSerialBus_SOURCE_DIR
                     SOURCES QtSerialBus_SRC
                     DROPPED_ENTRIES QtSerialBus_DROPPED_ENTRIES)
