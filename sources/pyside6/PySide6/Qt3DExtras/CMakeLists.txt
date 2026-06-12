# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(Qt3DExtras_SRC
${Qt3DExtras_GEN_DIR}/qt3dextras_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qabstractcameracontroller_inputstate_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qabstractcameracontroller_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qabstractspritesheet_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qconegeometry_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qconegeometryview_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qconemesh_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qcuboidgeometry_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qcuboidgeometryview_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qcuboidmesh_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qcylindergeometry_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qcylindergeometryview_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qcylindermesh_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qdiffusemapmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qdiffusespecularmapmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qdiffusespecularmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qextrudedtextgeometry_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qextrudedtextmesh_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qfirstpersoncameracontroller_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qforwardrenderer_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qgoochmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qmetalroughmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qmorphphongmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qnormaldiffusemapmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qnormaldiffusemapalphamaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qnormaldiffusespecularmapmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qorbitcameracontroller_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qpervertexcolormaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qphongmaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qphongalphamaterial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qplanegeometry_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qplanegeometryview_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qplanemesh_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qskyboxentity_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qspheregeometry_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qspheregeometryview_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qspheremesh_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qspritegrid_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qspritesheet_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qspritesheetitem_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qtext2dentity_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qtexturematerial_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qtorusgeometry_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qtorusgeometryview_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qtorusmesh_wrapper.cpp
${Qt3DExtras_GEN_DIR}/qt3dextras_qt3dwindow_wrapper.cpp
# module is always needed
${Qt3DExtras_GEN_DIR}/qt3dextras_module_wrapper.cpp)


set(Qt3DExtras_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtOpenGL_GEN_DIR}
    ${Qt3DCore_GEN_DIR}
    ${Qt3DRender_GEN_DIR}
)

set(Qt3DExtras_libraries
    Qt::3DExtras
)

set(Qt3DExtras_deps Qt3DRender)

create_pyside_module(NAME Qt3DExtras
                     INCLUDE_DIRS Qt3DExtras_include_dirs
                     LIBRARIES Qt3DExtras_libraries
                     DEPS Qt3DExtras_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES Qt3DExtras_SRC
                     TYPESYSTEM_NAME "${CMAKE_CURRENT_BINARY_DIR}/typesystem_3dextras.xml")
