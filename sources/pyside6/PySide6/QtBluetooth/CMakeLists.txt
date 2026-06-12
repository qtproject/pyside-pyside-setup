# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtBluetooth_OPTIONAL_SRC )
set(QtBluetooth_DROPPED_ENTRIES )

set(QtBluetooth_SRC
    ${QtBluetooth_GEN_DIR}/qbluetooth_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothaddress_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothdevicediscoveryagent_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothdeviceinfo_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothhostinfo_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothlocaldevice_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothserver_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothservicediscoveryagent_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothserviceinfo_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothserviceinfo_alternative_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothserviceinfo_sequence_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothsocket_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qbluetoothuuid_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergyadvertisingdata_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergyadvertisingparameters_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergyadvertisingparameters_addressinfo_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergycharacteristic_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergycharacteristicdata_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergyconnectionparameters_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergycontroller_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergydescriptor_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergydescriptordata_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergyservice_wrapper.cpp
    ${QtBluetooth_GEN_DIR}/qlowenergyservicedata_wrapper.cpp
# module is always needed
    ${QtBluetooth_GEN_DIR}/qtbluetooth_module_wrapper.cpp
)

set(QtBluetooth_include_dirs
    ${QtCore_GEN_DIR}
)

set(QtBluetooth_deps
    QtCore
)

set(QtBluetooth_libraries
    Qt::Bluetooth
)

create_pyside_module(NAME QtBluetooth
                     INCLUDE_DIRS QtBluetooth_include_dirs
                     LIBRARIES QtBluetooth_libraries
                     DEPS QtBluetooth_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtBluetooth_SRC
                     DROPPED_ENTRIES QtBluetooth_DROPPED_ENTRIES)
