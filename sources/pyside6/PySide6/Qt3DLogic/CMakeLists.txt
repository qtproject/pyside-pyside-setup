# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(Qt3DLogic_SRC
${Qt3DLogic_GEN_DIR}/qt3dlogic_wrapper.cpp
${Qt3DLogic_GEN_DIR}/qt3dlogic_qframeaction_wrapper.cpp
${Qt3DLogic_GEN_DIR}/qt3dlogic_qlogicaspect_wrapper.cpp
# module is always needed
${Qt3DLogic_GEN_DIR}/qt3dlogic_module_wrapper.cpp)

set(Qt3DLogic_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${Qt3DCore_GEN_DIR}
)

set(Qt3DLogic_libraries
    Qt::3DLogic
)

set(Qt3DLogic_deps Qt3DCore)

create_pyside_module(NAME Qt3DLogic
                     INCLUDE_DIRS Qt3DLogic_include_dirs
                     LIBRARIES Qt3DLogic_libraries
                     DEPS Qt3DLogic_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES Qt3DLogic_SRC
                     TYPESYSTEM_NAME "${CMAKE_CURRENT_BINARY_DIR}/typesystem_3dlogic.xml")
