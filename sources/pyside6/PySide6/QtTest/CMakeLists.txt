# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtTest_SRC
${QtTest_GEN_DIR}/qtest_pysideqtoucheventsequence_wrapper.cpp
${QtTest_GEN_DIR}/qabstractitemmodeltester_wrapper.cpp
${QtTest_GEN_DIR}/qsignalspy_wrapper.cpp
${QtTest_GEN_DIR}/qtest_wrapper.cpp
# module is always needed
${QtTest_GEN_DIR}/qttest_module_wrapper.cpp
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/QtTest_global.pre.h.in"
               "${CMAKE_CURRENT_BINARY_DIR}/QtTest_global.pre.h" @ONLY)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/QtTest_global.post.h.in"
               "${CMAKE_CURRENT_BINARY_DIR}/QtTest_global.post.h" @ONLY)

set(QtTest_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtWidgets_GEN_DIR}
)

set(QtTest_deps
    QtWidgets
)

# Link to QtGui/QtWidgets to enable gui/widget-specific inline functions
set(QtTest_libraries
    Qt::Test
    Qt::Widgets
    Qt::Gui
    Qt::Core
)

create_pyside_module(NAME QtTest
                     INCLUDE_DIRS QtTest_include_dirs
                     LIBRARIES QtTest_libraries
                     DEPS QtTest_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtTest_SRC)
