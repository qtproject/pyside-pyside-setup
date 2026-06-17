# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(Qt3DCore)

set(Qt3DCore_SRC
${Qt3DCore_GEN_DIR}/qsharedpointer_qaspectjob_wrapper.cpp
${Qt3DCore_GEN_DIR}/qsharedpointer_qbackendnodemapper_wrapper.cpp
${Qt3DCore_GEN_DIR}/qsharedpointer_qentity_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qabstractaspect_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qabstractfunctor_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qabstractskeleton_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qarmature_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qaspectengine_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qaspectjob_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qattribute_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qbackendnode_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qbackendnodemapper_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qboundingvolume_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qbuffer_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qcomponent_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qcoreaspect_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qcoresettings_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qentity_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qgeometry_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qgeometryview_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qjoint_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qnode_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qnodeid_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qnodeidtypepair_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qskeleton_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qskeletonloader_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_qtransform_wrapper.cpp
${Qt3DCore_GEN_DIR}/qt3dcore_wrapper.cpp
# module is always needed
${Qt3DCore_GEN_DIR}/qt3dcore_module_wrapper.cpp)

set(Qt3DCore_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtNetwork_GEN_DIR}
)

set(Qt3DCore_libraries
    Qt::3DCore
)

set(Qt3DCore_deps QtGui QtNetwork)

create_pyside_module(NAME Qt3DCore
                     INCLUDE_DIRS Qt3DCore_include_dirs
                     LIBRARIES Qt3DCore_libraries
                     DEPS Qt3DCore_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES Qt3DCore_SRC
                     TYPESYSTEM_NAME "${CMAKE_CURRENT_BINARY_DIR}/typesystem_3dcore.xml")
