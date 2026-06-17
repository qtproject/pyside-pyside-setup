# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtConcurrent)

set(QtConcurrent_SRC
${QtConcurrent_GEN_DIR}/qtconcurrent_wrapper.cpp
${QtConcurrent_GEN_DIR}/qfuturevoid_wrapper.cpp
${QtConcurrent_GEN_DIR}/qfutureqstring_wrapper.cpp
${QtConcurrent_GEN_DIR}/qfuturewatchervoid_wrapper.cpp
${QtConcurrent_GEN_DIR}/qfuturewatcherqstring_wrapper.cpp
# module is always needed
${QtConcurrent_GEN_DIR}/qtconcurrent_module_wrapper.cpp
)

set(QtConcurrent_include_dirs
    ${QtCore_GEN_DIR}
)

set(QtConcurrent_deps
    QtCore
)

set(QtConcurrent_libraries
    Qt::Concurrent
)

create_pyside_module(NAME QtConcurrent
                     INCLUDE_DIRS QtConcurrent_include_dirs
                     LIBRARIES QtConcurrent_libraries
                     DEPS QtConcurrent_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtConcurrent_SRC)
