project(QtBluetooth)

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
    #    ${QtBluetooth_GEN_DIR}/qbluetoothserviceinfo_alternative_wrapper.cpp
    #    ${QtBluetooth_GEN_DIR}/qbluetoothserviceinfo_sequence_wrapper.cpp
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

set(QtBluetooth_include_dirs ${QtBluetooth_SOURCE_DIR}
                             ${QtBluetooth_BINARY_DIR}
                             ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                             ${Qt${QT_MAJOR_VERSION}Bluetooth_INCLUDE_DIRS}
                             ${libpyside_SOURCE_DIR}
                             ${QtCore_GEN_DIR})

set(QtBluetooth_libraries pyside6
                        ${Qt${QT_MAJOR_VERSION}Bluetooth_LIBRARIES})

set(QtBluetooth_deps QtCore)

create_pyside_module(NAME QtBluetooth
                     INCLUDE_DIRS QtBluetooth_include_dirs
                     LIBRARIES QtBluetooth_libraries
                     DEPS QtBluetooth_deps
                     TYPESYSTEM_PATH QtBluetooth_SOURCE_DIR
                     SOURCES QtBluetooth_SRC
                     DROPPED_ENTRIES QtBluetooth_DROPPED_ENTRIES)
