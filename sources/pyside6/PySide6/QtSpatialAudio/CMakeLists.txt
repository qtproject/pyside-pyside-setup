# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtSpatialAudio)

set(QtSpatialAudio_SRC
${QtSpatialAudio_GEN_DIR}/qambientsound_wrapper.cpp
${QtSpatialAudio_GEN_DIR}/qaudioengine_wrapper.cpp
${QtSpatialAudio_GEN_DIR}/qaudiolistener_wrapper.cpp
${QtSpatialAudio_GEN_DIR}/qaudioroom_wrapper.cpp
${QtSpatialAudio_GEN_DIR}/qspatialsound_wrapper.cpp

# module is always needed
${QtSpatialAudio_GEN_DIR}/qtspatialaudio_module_wrapper.cpp
)

set(QtSpatialAudio_include_dirs ${QtSpatialAudio_SOURCE_DIR}
                                ${QtSpatialAudio_BINARY_DIR}
                                ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                                ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                                ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                                ${Qt${QT_MAJOR_VERSION}Multimedia_INCLUDE_DIRS}
                                ${Qt${QT_MAJOR_VERSION}SpatialAudio_INCLUDE_DIRS}
                                ${libpyside_SOURCE_DIR}
                                ${QtCore_GEN_DIR}
                                ${QtGui_GEN_DIR}
                                ${QtNetwork_GEN_DIR}
                                ${QtMultimedia_GEN_DIR})

set(QtSpatialAudio_libraries pyside6
                             ${Qt${QT_MAJOR_VERSION}SpatialAudio_LIBRARIES}
                             ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                             ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
                             ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES}
                             ${Qt${QT_MAJOR_VERSION}Multimedia_LIBRARIES}
                             )
set(QtSpatialAudio_deps QtCore QtGui QtNetwork QtMultimedia)

create_pyside_module(NAME QtSpatialAudio
                     INCLUDE_DIRS QtSpatialAudio_include_dirs
                     LIBRARIES QtSpatialAudio_libraries
                     DEPS QtSpatialAudio_deps
                     TYPESYSTEM_PATH QtSpatialAudio_SOURCE_DIR
                     SOURCES QtSpatialAudio_SRC)
