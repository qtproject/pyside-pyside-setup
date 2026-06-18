# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtAxContainer)

set(QtAxContainer_SRC
${QtAxContainer_GEN_DIR}/qaxbase_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxbaseobject_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxbasewidget_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxobject_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxobjectinterface_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxscript_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxscriptengine_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxscriptmanager_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxselect_wrapper.cpp
${QtAxContainer_GEN_DIR}/qaxwidget_wrapper.cpp
# module is always needed
${QtAxContainer_GEN_DIR}/qtaxcontainer_module_wrapper.cpp)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/QtAxContainer_global.post.h.in"
               "${CMAKE_CURRENT_BINARY_DIR}/QtAxContainer_global.post.h" @ONLY)

set(QtAxContainer_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtWidgets_GEN_DIR}
)

set(QtAxContainer_deps
    QtWidgets
)

set(QtAxContainer_libraries
    Qt::AxContainer
)

create_pyside_module(NAME QtAxContainer
                     INCLUDE_DIRS QtAxContainer_include_dirs
                     LIBRARIES QtAxContainer_libraries
                     DEPS QtAxContainer_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtAxContainer_SRC
                     TYPESYSTEM_NAME "${CMAKE_CURRENT_BINARY_DIR}/typesystem_axcontainer.xml")
