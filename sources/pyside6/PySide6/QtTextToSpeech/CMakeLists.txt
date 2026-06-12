# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtTextToSpeech_SRC
${QtTextToSpeech_GEN_DIR}/qtexttospeech_wrapper.cpp
${QtTextToSpeech_GEN_DIR}/qtexttospeechengine_wrapper.cpp
${QtTextToSpeech_GEN_DIR}/qvoice_wrapper.cpp
# module is always needed
${QtTextToSpeech_GEN_DIR}/qttexttospeech_module_wrapper.cpp
)

set(QtTextToSpeech_include_dirs
    ${QtCore_GEN_DIR}
)

set(QtTextToSpeech_deps
    QtCore
    QtMultimedia
)

set(QtTextToSpeech_libraries
    Qt::TextToSpeech
)

create_pyside_module(NAME QtTextToSpeech
                     INCLUDE_DIRS QtTextToSpeech_include_dirs
                     LIBRARIES QtTextToSpeech_libraries
                     DEPS QtTextToSpeech_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtTextToSpeech_SRC)
