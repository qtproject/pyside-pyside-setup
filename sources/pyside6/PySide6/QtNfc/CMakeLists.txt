project(QtNfc)

set(QtNfc_SRC
    ${QtNfc_GEN_DIR}/qndeffilter_record_wrapper.cpp
    ${QtNfc_GEN_DIR}/qndeffilter_wrapper.cpp
    ${QtNfc_GEN_DIR}/qndefmessage_wrapper.cpp
    ${QtNfc_GEN_DIR}/qndefnfciconrecord_wrapper.cpp
    ${QtNfc_GEN_DIR}/qndefnfcsmartposterrecord_wrapper.cpp
    ${QtNfc_GEN_DIR}/qndefrecord_wrapper.cpp
    ${QtNfc_GEN_DIR}/qndefnfctextrecord_wrapper.cpp
    ${QtNfc_GEN_DIR}/qndefnfcurirecord_wrapper.cpp
    ${QtNfc_GEN_DIR}/qnearfieldmanager_wrapper.cpp
    ${QtNfc_GEN_DIR}/qnearfieldtarget_wrapper.cpp
# module is always needed
    ${QtNfc_GEN_DIR}/qtnfc_module_wrapper.cpp)

set(QtNfc_include_dirs ${QtNfc_SOURCE_DIR}
                       ${QtNfc_BINARY_DIR}
                       ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                       ${Qt${QT_MAJOR_VERSION}Nfc_INCLUDE_DIRS}
                       ${libpyside_SOURCE_DIR}
                       ${QtCore_GEN_DIR})

set(QtNfc_libraries pyside6
    ${Qt${QT_MAJOR_VERSION}Nfc_LIBRARIES})

set(QtNfc_deps QtCore)

create_pyside_module(NAME QtNfc
                     INCLUDE_DIRS QtNfc_include_dirs
                     LIBRARIES QtNfc_libraries
                     DEPS QtNfc_deps
                     TYPESYSTEM_PATH QtNfc_SOURCE_DIR
                     SOURCES QtNfc_SRC)
