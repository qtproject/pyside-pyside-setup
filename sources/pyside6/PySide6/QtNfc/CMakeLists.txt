# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

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
    ${QtNfc_GEN_DIR}/qnearfieldtarget_requestid_wrapper.cpp
# module is always needed
    ${QtNfc_GEN_DIR}/qtnfc_module_wrapper.cpp)

set(QtNfc_include_dirs
    ${QtCore_GEN_DIR}
)

set(QtNfc_deps
    QtCore
)

set(QtNfc_libraries
    Qt::Nfc
)

create_pyside_module(NAME QtNfc
                     INCLUDE_DIRS QtNfc_include_dirs
                     LIBRARIES QtNfc_libraries
                     DEPS QtNfc_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtNfc_SRC)
