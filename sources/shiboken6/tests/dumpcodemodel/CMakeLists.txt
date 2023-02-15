# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

add_executable(dumpcodemodel main.cpp)

target_include_directories(dumpcodemodel
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/../../ApiExtractor
)

target_link_libraries(dumpcodemodel
    PRIVATE
        apiextractor
        Qt::Core
)
