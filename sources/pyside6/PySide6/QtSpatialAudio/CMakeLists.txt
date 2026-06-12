# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtSpatialAudio_SRC
${QtSpatialAudio_GEN_DIR}/qambientsound_wrapper.cpp
${QtSpatialAudio_GEN_DIR}/qaudioengine_wrapper.cpp
${QtSpatialAudio_GEN_DIR}/qaudiolistener_wrapper.cpp
${QtSpatialAudio_GEN_DIR}/qaudioroom_wrapper.cpp
${QtSpatialAudio_GEN_DIR}/qspatialsound_wrapper.cpp

# module is always needed
${QtSpatialAudio_GEN_DIR}/qtspatialaudio_module_wrapper.cpp
)

set(QtSpatialAudio_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtMultimedia_GEN_DIR}
)

set(QtSpatialAudio_deps
    QtCore
    QtGui
    QtNetwork
    QtMultimedia
)

set(QtSpatialAudio_libraries
    Qt::SpatialAudio
)

create_pyside_module(NAME QtSpatialAudio
                     INCLUDE_DIRS QtSpatialAudio_include_dirs
                     LIBRARIES QtSpatialAudio_libraries
                     DEPS QtSpatialAudio_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtSpatialAudio_SRC)
