# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtQml)

qt_wrap_cpp(QPYQMLPARSERSTATUS_MOC "${PYSIDE_PACKAGE_SOURCE_DIR}/qpyqmlparserstatus.h")
qt_wrap_cpp(QPYQMLPROPERTYVALUESOURCE_MOC "${PYSIDE_PACKAGE_SOURCE_DIR}/qpyqmlpropertyvaluesource.h")

set(QtQml_static_sources "${CMAKE_CURRENT_SOURCE_DIR}/pysideqmlvolatilebool.cpp"
                         "${QPYQMLPARSERSTATUS_MOC}"
                         "${QPYQMLPROPERTYVALUESOURCE_MOC}")

set(QtQml_SRC
${QtQml_GEN_DIR}/qjsengine_wrapper.cpp
${QtQml_GEN_DIR}/qjsmanagedvalue_wrapper.cpp
${QtQml_GEN_DIR}/qjsprimitivevalue_wrapper.cpp
${QtQml_GEN_DIR}/qjsvalue_wrapper.cpp
${QtQml_GEN_DIR}/qjsvalueiterator_wrapper.cpp
${QtQml_GEN_DIR}/qpyqmlparserstatus_wrapper.cpp
${QtQml_GEN_DIR}/qpyqmlpropertyvaluesource_wrapper.cpp
${QtQml_GEN_DIR}/qqmlabstracturlinterceptor_wrapper.cpp
${QtQml_GEN_DIR}/qqmlapplicationengine_wrapper.cpp
${QtQml_GEN_DIR}/qqmlcomponent_wrapper.cpp
${QtQml_GEN_DIR}/qqmlcontext_wrapper.cpp
${QtQml_GEN_DIR}/qqmlcontext_propertypair_wrapper.cpp
${QtQml_GEN_DIR}/qqmlerror_wrapper.cpp
${QtQml_GEN_DIR}/qqmldebuggingenabler_wrapper.cpp
${QtQml_GEN_DIR}/qqmlengine_wrapper.cpp
${QtQml_GEN_DIR}/qqmlexpression_wrapper.cpp
${QtQml_GEN_DIR}/qqmlextensioninterface_wrapper.cpp
${QtQml_GEN_DIR}/qqmltypesextensioninterface_wrapper.cpp
${QtQml_GEN_DIR}/qqmlextensionplugin_wrapper.cpp
${QtQml_GEN_DIR}/qqmlfile_wrapper.cpp
${QtQml_GEN_DIR}/qqmlfileselector_wrapper.cpp
${QtQml_GEN_DIR}/qqmlimageproviderbase_wrapper.cpp
${QtQml_GEN_DIR}/qqmlincubator_wrapper.cpp
${QtQml_GEN_DIR}/qqmlincubationcontroller_wrapper.cpp
#${QtQml_GEN_DIR}/qqmllistproperty_wrapper.cpp
${QtQml_GEN_DIR}/qqmllistreference_wrapper.cpp
${QtQml_GEN_DIR}/qqmlparserstatus_wrapper.cpp
${QtQml_GEN_DIR}/qqmlproperty_wrapper.cpp
${QtQml_GEN_DIR}/qqmlpropertymap_wrapper.cpp
${QtQml_GEN_DIR}/qqmlpropertyvaluesource_wrapper.cpp
${QtQml_GEN_DIR}/qqmlscriptstring_wrapper.cpp
${QtQml_GEN_DIR}/qqmlnetworkaccessmanagerfactory_wrapper.cpp
# module is always needed
${QtQml_GEN_DIR}/qtqml_module_wrapper.cpp
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/QtQml_global.post.h.in"
               "${CMAKE_CURRENT_BINARY_DIR}/QtQml_global.post.h" @ONLY)

set(QtQml_include_dirs
    ${QtCore_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtQml_GEN_DIR}
)

set(QtQml_deps
    QtNetwork
)

set(QtQml_libraries
    PySide6::pyside6qml
    Qt::CorePrivate
    Qt::Qml
)

create_pyside_module(NAME QtQml
                     INCLUDE_DIRS QtQml_include_dirs
                     LIBRARIES QtQml_libraries
                     DEPS QtQml_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtQml_SRC
                     STATIC_SOURCES QtQml_static_sources)
